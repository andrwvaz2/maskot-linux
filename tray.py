"""Ícono en la bandeja del sistema vía StatusNotifierItem (DBus).

libayatana-appindicator es una librería GTK3: construiría un `Gtk.Menu` de
GTK3, pero esta app es GTK4 y PyGObject no permite cargar dos versiones del
mismo namespace ("Gtk") en un proceso. Por eso aquí hablamos directamente el
protocolo StatusNotifierItem sobre DBus con Gio (sin dependencias extra). Es el
mismo protocolo que consume libayatana-appindicator, así que funciona con
cualquier host SNI (KDE, GNOME con extensión, barras de Sway/niri, etc.).

Si no hay bus de sesión o el host SNI no está, se avisa por consola y la app
sigue funcionando sin ícono (fallback, no crashea).
"""

from __future__ import annotations

import os

import gi

gi.require_version("Gio", "2.0")
from gi.repository import Gio, GLib  # noqa: E402

# --- Introspección XML de las interfaces ------------------------------------

SNI_ITEM_XML = """
<node>
  <interface name="org.kde.StatusNotifierItem">
    <property name="Category" type="s" access="read"/>
    <property name="Id" type="s" access="read"/>
    <property name="Title" type="s" access="read"/>
    <property name="Status" type="s" access="read"/>
    <property name="IconName" type="s" access="read"/>
    <property name="IconThemePath" type="s" access="read"/>
    <property name="ItemIsMenu" type="b" access="read"/>
    <property name="Menu" type="o" access="read"/>
    <method name="Activate">
      <arg type="i" direction="in" name="x"/>
      <arg type="i" direction="in" name="y"/>
    </method>
    <method name="SecondaryActivate">
      <arg type="i" direction="in" name="x"/>
      <arg type="i" direction="in" name="y"/>
    </method>
    <method name="ContextMenu">
      <arg type="i" direction="in" name="x"/>
      <arg type="i" direction="in" name="y"/>
    </method>
  </interface>
</node>
"""

DBUSMENU_XML = """
<node>
  <interface name="com.canonical.dbusmenu">
    <property name="Version" type="u" access="read"/>
    <property name="TextDirection" type="s" access="read"/>
    <property name="Status" type="s" access="read"/>
    <property name="IconThemePath" type="as" access="read"/>
    <method name="GetLayout">
      <arg type="i" direction="in" name="parentId"/>
      <arg type="i" direction="in" name="recursionDepth"/>
      <arg type="as" direction="in" name="propertyNames"/>
      <arg type="u" direction="out" name="revision"/>
      <arg type="a(ia{sv}av)" direction="out" name="layout"/>
    </method>
    <method name="GetGroupProperties">
      <arg type="ai" direction="in" name="ids"/>
      <arg type="as" direction="in" name="propertyNames"/>
      <arg type="a(ia{sv})" direction="out" name="properties"/>
    </method>
    <method name="GetProperty">
      <arg type="i" direction="in" name="id"/>
      <arg type="s" direction="in" name="name"/>
      <arg type="v" direction="out" name="value"/>
    </method>
    <method name="Event">
      <arg type="i" direction="in" name="id"/>
      <arg type="s" direction="in" name="eventId"/>
      <arg type="v" direction="in" name="data"/>
      <arg type="u" direction="in" name="timestamp"/>
    </method>
    <method name="AboutToShow">
      <arg type="i" direction="in" name="id"/>
      <arg type="b" direction="out" name="needUpdate"/>
    </method>
  </interface>
</node>
"""

# IDs de los elementos del menú.
ID_TOGGLE = 1
ID_QUIT = 2


class Tray:
    """Ícono SNI con menú de dos entradas: Ocultar/Mostrar y Salir."""

    def __init__(self, on_toggle=None, on_quit=None):
        self.on_toggle = on_toggle
        self.on_quit = on_quit
        self.visible = True

        self.connection = None
        self.unique_name = None
        self.well_known = None
        self.own_id = 0
        self.item_reg_id = 0
        self.menu_reg_id = 0
        self._node_infos = []

        self._init()

    # -- inicialización -----------------------------------------------------

    def _init(self):
        try:
            self.connection = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        except Exception as exc:  # noqa: BLE001 - queremos no crashear
            print(f"[tray] sin bus de sesión DBus; se omite el ícono: {exc}")
            return
        if self.connection is None:
            print("[tray] no hay conexión al bus de sesión; se omite el ícono")
            return

        self.well_known = f"org.kde.StatusNotifierItem-{os.getpid()}-1"

        self.own_id = Gio.bus_own_name_on_connection(
            self.connection,
            self.well_known,
            Gio.BusNameOwnerFlags.NONE,
            self._on_name_acquired,
            self._on_name_lost,
        )

        item_info = Gio.DBusNodeInfo.new_for_xml(SNI_ITEM_XML).interfaces[0]
        menu_info = Gio.DBusNodeInfo.new_for_xml(DBUSMENU_XML).interfaces[0]
        self._node_infos = [item_info, menu_info]

        self.item_reg_id = self.connection.register_object(
            "/StatusNotifierItem", item_info,
            self._method_call_item, self._get_prop_item, None,
        )
        self.menu_reg_id = self.connection.register_object(
            "/MenuBar", menu_info,
            self._method_call_menu, self._get_prop_menu, None,
        )

        self._register_with_watcher()
        print("[tray] StatusNotifierItem registrado en el bus de sesión")

    def _register_with_watcher(self):
        # El watcher resuelve el nombre (o ruta) y busca /StatusNotifierItem.
        target = self.unique_name or self.well_known
        try:
            self.connection.call_sync(
                "org.kde.StatusNotifierWatcher",
                "/StatusNotifierWatcher",
                "org.kde.StatusNotifierWatcher",
                "RegisterStatusNotifierItem",
                GLib.Variant("(s)", (target,)),
                None,
                Gio.DBusCallFlags.NONE,
                -1,
                None,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"[tray] no se pudo registrar con el watcher SNI: {exc}")

    # -- callbacks de nombres ----------------------------------------------

    def _on_name_acquired(self, connection, name):
        self.unique_name = connection.get_unique_name()

    def _on_name_lost(self, connection, name):
        print("[tray] se perdió el nombre DBus; el ícono dejará de verse")

    # -- interfaz org.kde.StatusNotifierItem --------------------------------

    def _get_prop_item(self, connection, sender, object_path, interface, prop):
        props = {
            "Category": GLib.Variant("s", "ApplicationStatus"),
            "Id": GLib.Variant("s", "mascota"),
            "Title": GLib.Variant("s", "Mascota"),
            "Status": GLib.Variant("s", "Active"),
            "IconName": GLib.Variant("s", "face-smile"),
            "IconThemePath": GLib.Variant("s", ""),
            "ItemIsMenu": GLib.Variant("b", False),
            "Menu": GLib.Variant("o", "/MenuBar"),
        }
        return props.get(prop, GLib.Variant("s", ""))

    def _method_call_item(self, connection, sender, object_path, interface,
                          method, params, invocation):
        if method == "Activate":
            self._toggle()
            invocation.return_value(GLib.Variant("()", ()))
        elif method in ("SecondaryActivate", "ContextMenu"):
            # El host ya muestra el menú por la propiedad Menu.
            invocation.return_value(GLib.Variant("()", ()))
        else:
            invocation.return_dbus_error(
                "org.freedesktop.DBus.Error.UnknownMethod",
                f"método desconocido: {method}",
            )

    # -- interfaz com.canonical.dbusmenu -----------------------------------

    def _get_prop_menu(self, connection, sender, object_path, interface, prop):
        props = {
            "Version": GLib.Variant("u", 3),
            "TextDirection": GLib.Variant("s", "ltr"),
            "Status": GLib.Variant("s", "normal"),
            "IconThemePath": GLib.Variant("as", []),
        }
        return props.get(prop, GLib.Variant("u", 0))

    def _method_call_menu(self, connection, sender, object_path, interface,
                          method, params, invocation):
        if method == "GetLayout":
            _, _, _ = params.unpack()
            revision = 1
            layout = self._build_layout()
            invocation.return_value(
                GLib.Variant("(ua(ia{sv}av))", (revision, layout))
            )
        elif method == "GetGroupProperties":
            invocation.return_value(GLib.Variant("(a(ia{sv}))", ([],)))
        elif method == "GetProperty":
            item_id, name = params.unpack()
            invocation.return_value(
                GLib.Variant("(v)", (self._menu_prop(item_id, name),))
            )
        elif method == "Event":
            item_id, event, _, _ = params.unpack()
            self._handle_event(item_id, event)
            invocation.return_value(GLib.Variant("()", ()))
        elif method == "AboutToShow":
            invocation.return_value(GLib.Variant("(b)", (False,)))
        else:
            invocation.return_dbus_error(
                "org.freedesktop.DBus.Error.UnknownMethod",
                f"método desconocido: {method}",
            )

    def _make_item(self, item_id, props):
        # Elemento de menú como GLib.Variant (ia{sv}av); se usa como hijo en
        # el árbol (el tipo `av` requiere Variants ya envueltos).
        return GLib.Variant("(ia{sv}av)", (item_id, props, []))

    def _build_layout(self):
        """Devuelve el layout como lista con un único elemento (la raíz).

        La raíz es una tupla cruda (0, {}, [hijos]) porque `a(ia{sv}av)` espera
        tuplas, mientras que los hijos ya son GLib.Variant (requerido por `av`).
        """
        label_toggle = "Ocultar" if self.visible else "Mostrar"
        item_toggle = self._make_item(ID_TOGGLE, {
            "label": GLib.Variant("s", label_toggle),
            "enabled": GLib.Variant("b", True),
        })
        item_quit = self._make_item(ID_QUIT, {
            "label": GLib.Variant("s", "Salir"),
            "enabled": GLib.Variant("b", True),
        })
        root = (0, {}, [item_toggle, item_quit])
        return [root]

    def _menu_prop(self, item_id, name):
        if name == "enabled":
            return GLib.Variant("b", True)
        if item_id == ID_TOGGLE:
            label = "Ocultar" if self.visible else "Mostrar"
        elif item_id == ID_QUIT:
            label = "Salir"
        else:
            return GLib.Variant("s", "")
        return GLib.Variant("s", label)

    def _handle_event(self, item_id, event):
        if event != "clicked":
            return
        if item_id == ID_TOGGLE:
            self._toggle()
        elif item_id == ID_QUIT:
            if self.on_quit:
                self.on_quit()

    # -- acciones -----------------------------------------------------------

    def _toggle(self):
        self.visible = not self.visible
        if self.on_toggle:
            self.on_toggle(self.visible)

    def shutdown(self):
        """Libera el nombre y los objetos (se usa al salir)."""
        if self.connection is None:
            return
        if self.own_id:
            Gio.bus_unown_name(self.own_id)
        if self.item_reg_id:
            self.connection.unregister_object(self.item_reg_id)
        if self.menu_reg_id:
            self.connection.unregister_object(self.menu_reg_id)

__id__ = "extera_custom_name_icon"
__name__ = "Custom Name & Icon"
__description__ = """**EN:** Allows you to set a custom name and icon for the client in the recent apps menu and on the launcher
**RU:** Позволяет установить кастомное имя и иконку клиента в меню недавних приложений и на рабочем столе"""
__version__ = "1.1"
__author__ = "@AlexeiCrystal"
__icon__ = "exteraGram/0"
__app_version__ = ">=11.12.0"
__sdk_version__ = ">=1.4.3.3"

import base64
from java.io import ByteArrayOutputStream
from java.util import Locale
from typing import Any, List

from org.telegram.messenger import ApplicationLoader
from org.telegram.messenger.browser import Browser

from android.app import Activity, ActivityManager
from android.os import Build
from android.content import Intent, ComponentName, Context
from android.content.pm import PackageManager, ShortcutManager, ShortcutInfo
from android.graphics import Bitmap, BitmapFactory
from android.graphics.drawable import Icon
from android.net import Uri

from base_plugin import BasePlugin, MethodHook
from client_utils import get_last_fragment
from hook_utils import find_class
from ui.settings import Input, Text, Header, Divider

strings = {
    "ru": {
        "client_name": "Имя клиента",
        "custom_name": "Кастомное имя",
        "enter_custom_client_name": "Введите кастомное имя клиента",
        "client_icon": "Иконка клиента",
        "select_custom_icon": "Выбрать кастомную иконку",
        "shortcut": "Ярлык",
        "create_shortcut": "Создать ярлык",
        "create_shortcut_info": "Для отображения кастомного имени и иконки на рабочем столе необходимо создать отдельный ярлык. Перед изменением не забудьте удалить старый созданный ярлык, если вы до этого его создавали",
        "reset_to_default": "Сбросить по умолчанию",
        "info": "Информация"
    },
    "en": {
        "client_name": "Client name",
        "custom_name": "Custom name",
        "enter_custom_client_name": "Enter custom client name",
        "client_icon": "Client icon",
        "select_custom_icon": "Select custom icon",
        "shortcut": "Shortcut",
        "create_shortcut": "Create shortcut",
        "create_shortcut_info": "To display a custom name and icon on the launcher, you need to create a separate shortcut. Before making any changes, don’t forget to delete the old shortcut, if you had created one previously",
        "reset_to_default": "Reset to default",
        "info": "Info"
    },
}

GITHUB_URL="https://github.com/AlexeiCrystal/extera-custom-name-icon"
PACKIT_URL="tg://packit?plugin=extera_custom_name_icon&repo=shareui_official"

REQUEST_PICK_IMAGE = 3721


def get_lang():
    if Locale.getDefault().getLanguage() == "ru":
        return "ru"
    else:
        return "en"

def get_str(key):
    return strings[get_lang()][key]


def get_application_context():
    return ApplicationLoader.applicationContext

def get_client_package():
    return get_application_context().getPackageName()

def get_client_name():
    context = get_application_context()
    return context.getString(context.getApplicationInfo().labelRes)

def get_current_activity():
    try:
        fragment = get_last_fragment()
        if fragment:
            return fragment.getParentActivity()
    except Exception:
        pass
    return None

def build_task_description(title: str, bitmap_icon: Bitmap = None):
    if Build.VERSION.SDK_INT >= 33:
        builder = ActivityManager.TaskDescription.Builder().setLabel(title)
        if bitmap_icon is not None:
            builder.setIcon(Icon.createWithBitmap(bitmap_icon))
        return builder.build()
    else:
        return ActivityManager.TaskDescription(title, bitmap_icon)

def set_task_description(activity, title: str, bitmap_icon: Bitmap = None):
    try:
        if activity is None:
            return
        task_desc = build_task_description(title, bitmap_icon)
        activity.setTaskDescription(task_desc)
    except Exception:
        pass


def crop_to_square(src_bitmap: Bitmap) -> Bitmap:
    if src_bitmap is None:
        return None
    try:
        w = src_bitmap.getWidth()
        h = src_bitmap.getHeight()

        if w == h:
            return src_bitmap

        if w > h:
            crop_size = h
            x = (w - h) // 2
            y = 0
        else:
            crop_size = w
            x = 0
            y = (h - w) // 2

        return Bitmap.createBitmap(src_bitmap, int(x), int(y), int(crop_size), int(crop_size))
    except Exception as e:
        return src_bitmap

def bitmap_to_base64(bitmap: Bitmap) -> str:
    if bitmap is None:
        return ""
    try:
        baos = ByteArrayOutputStream()
        bitmap.compress(Bitmap.CompressFormat.PNG, 100, baos)
        b_bytes = baos.toByteArray()
        return base64.b64encode(bytes(b_bytes)).decode("utf-8")
    except Exception:
        return ""

def base64_to_bitmap(b64_str: str) -> Bitmap:
    if not b64_str:
        return None
    try:
        img_bytes = base64.b64decode(b64_str)
        return BitmapFactory.decodeByteArray(img_bytes, 0, len(img_bytes))
    except Exception:
        return None

def pick_icon(v):
    activity = get_current_activity()
    if activity:
        intent = Intent(Intent.ACTION_PICK)
        intent.setType("image/*")
        activity.startActivityForResult(intent, REQUEST_PICK_IMAGE)

def create_shortcut(name: str, icon_bitmap: Bitmap = None):
    try:
        context = get_application_context()
        pm = context.getPackageManager()
        package_name = context.getPackageName()

        main_intent = Intent(Intent.ACTION_MAIN)
        main_intent.addCategory(Intent.CATEGORY_LAUNCHER)
        main_intent.setPackage(package_name)

        resolve_info = pm.resolveActivity(main_intent, 0)

        if resolve_info and resolve_info.activityInfo:
            active_activity_name = resolve_info.activityInfo.name
            active_icon_res_id = resolve_info.activityInfo.getIconResource()

            launch_intent = Intent(Intent.ACTION_MAIN)
            launch_intent.addCategory(Intent.CATEGORY_LAUNCHER)
            launch_intent.setComponent(ComponentName(package_name, active_activity_name))
        else:
            launch_intent = pm.getLaunchIntentForPackage(package_name)
            active_icon_res_id = context.getApplicationInfo().icon

        if launch_intent is None:
            launch_intent = Intent(Intent.ACTION_MAIN)
            launch_intent.addCategory(Intent.CATEGORY_LAUNCHER)
            launch_intent.setComponent(
                ComponentName(package_name, "org.telegram.ui.LaunchActivity")
            )

        launch_intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        launch_intent.addFlags(Intent.FLAG_ACTIVITY_RESET_TASK_IF_NEEDED)

        builder = ShortcutInfo.Builder(context, "custom_name_icon_plugin_" + str(abs(hash(name))))
        builder.setShortLabel(name)
        builder.setLongLabel(name)
        builder.setIntent(launch_intent)

        if icon_bitmap is not None:
            square_icon = crop_to_square(icon_bitmap)
            builder.setIcon(Icon.createWithBitmap(square_icon))
        else:
            if active_icon_res_id != 0:
                builder.setIcon(Icon.createWithResource(package_name, active_icon_res_id))

        shortcut_info = builder.build()
        shortcut_manager = context.getSystemService(Context.SHORTCUT_SERVICE)

        if shortcut_manager and shortcut_manager.isRequestPinShortcutSupported():
            shortcut_manager.requestPinShortcut(shortcut_info, None)
            return True
        return False

    except Exception as e:
        return False

def get_saved_icon(plugin) -> Bitmap:
    b64_str = plugin.get_setting("custom_client_icon", "")
    return base64_to_bitmap(b64_str)


class ActivityResultHook(MethodHook):
    def __init__(self, plugin):
        self.plugin = plugin
        super().__init__()

    def after_hooked_method(self, param):
        try:
            request_code = param.args[0]
            result_code = param.args[1]
            data = param.args[2]

            if request_code != REQUEST_PICK_IMAGE:
                return
            if result_code != Activity.RESULT_OK or data is None:
                return

            uri = data.getData()
            if uri is None:
                return

            self.plugin._handle_image_picked(uri)
        except Exception:
            pass

class SetTaskDescriptionInterceptor(MethodHook):
    def __init__(self, plugin):
        self.plugin = plugin
        super().__init__()

    def before_hooked_method(self, param):
        try:
            if param.args and len(param.args) > 0:
                title = self.plugin.get_setting("custom_client_name", get_client_name())
                icon = get_saved_icon(self.plugin)
                param.args[0] = build_task_description(title, icon)
        except Exception:
            pass

class ActivityLifecycleHook(MethodHook):
    def __init__(self, plugin):
        self.plugin = plugin
        super().__init__()

    def after_hooked_method(self, param):
        activity = param.thisObject
        if activity:
            title = self.plugin.get_setting("custom_client_name", get_client_name())
            icon = get_saved_icon(self.plugin)
            set_task_description(activity, title, icon)

class FragmentLifecycleHook(MethodHook):
    def __init__(self, plugin):
        self.plugin = plugin
        super().__init__()

    def after_hooked_method(self, param):
        fragment = param.thisObject
        if fragment:
            try:
                activity = fragment.getParentActivity()
                if activity:
                    title = self.plugin.get_setting("custom_client_name", get_client_name())
                    icon = get_saved_icon(self.plugin)
                    set_task_description(activity, title, icon)
            except Exception:
                pass


class ExteraCustomNameIconPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.unhook_list = []
        self.hooked_classes = set()

    def _hook_activity_class(self, clazz):
        if not clazz or clazz in self.hooked_classes:
            return

        class_name = clazz.getName()

        hooks_td = self.hook_all_methods(clazz, "setTaskDescription", SetTaskDescriptionInterceptor(self))
        if hooks_td:
            self.unhook_list.extend(hooks_td)

        hooks_create = self.hook_all_methods(clazz, "onCreate", ActivityLifecycleHook(self))
        if hooks_create:
            self.unhook_list.extend(hooks_create)

        hooks_resume = self.hook_all_methods(clazz, "onResume", ActivityLifecycleHook(self))
        if hooks_resume:
            self.unhook_list.extend(hooks_resume)

        self.hooked_classes.add(clazz)

    def _handle_image_picked(self, uri):
        try:
            context = get_application_context()
            input_stream = context.getContentResolver().openInputStream(uri)
            bitmap = BitmapFactory.decodeStream(input_stream)
            input_stream.close()

            if bitmap is None:
                return

            b64 = bitmap_to_base64(bitmap)
            self.set_setting("custom_client_icon", b64, reload_settings=True)

            set_task_description(
                get_current_activity(),
                self.get_setting("custom_client_name", get_client_name()),
                bitmap
            )
        except Exception as e:
            pass

    def on_plugin_load(self):
        title = self.get_setting("custom_client_name", get_client_name())
        icon = get_saved_icon(self)
        set_task_description(get_current_activity(), title, icon)

        LaunchActivityClass = find_class("org.telegram.ui.LaunchActivity")
        if LaunchActivityClass is not None:
            hooks_ar = self.hook_all_methods(LaunchActivityClass, "onActivityResult", ActivityResultHook(self))
            if hooks_ar:
                self.unhook_list.extend(hooks_ar)

        BaseFragment = find_class("org.telegram.ui.ActionBar.BaseFragment")
        if BaseFragment:
            hooks_frag_resume = self.hook_all_methods(BaseFragment, "onResume", FragmentLifecycleHook(self))
            if hooks_frag_resume:
                self.unhook_list.extend(hooks_frag_resume)

            hooks_frag_create = self.hook_all_methods(BaseFragment, "onFragmentCreate", FragmentLifecycleHook(self))
            if hooks_frag_create:
                self.unhook_list.extend(hooks_frag_create)

        ActivityBase = find_class("android.app.Activity")
        ClassLoaderClass = find_class("java.lang.ClassLoader")

        if ActivityBase and ClassLoaderClass:
            plugin_self = self

            class ClassLoaderHook(MethodHook):
                def after_hooked_method(self, param):
                    try:
                        loaded_class = param.getResult()
                        if loaded_class and issubclass(loaded_class, ActivityBase):
                            plugin_self._hook_activity_class(loaded_class)
                    except Exception:
                        pass

            hooks_cl = self.hook_all_methods(ClassLoaderClass, "loadClass", ClassLoaderHook())
            if hooks_cl:
                self.unhook_list.extend(hooks_cl)

    def on_plugin_unload(self):
        if self.unhook_list:
            for unhook in self.unhook_list:
                try:
                    unhook.unhook()
                except Exception:
                    pass
            self.unhook_list.clear()
            self.hooked_classes.clear()
        set_task_description(get_current_activity(), get_client_name(), None)


    def on_client_name_input_change(self, custom_client_name: str):
        self.set_setting("custom_client_name", custom_client_name, reload_settings=True)
        set_task_description(get_current_activity(), custom_client_name, get_saved_icon(self))

    def on_client_name_reset(self, v):
        self.set_setting("custom_client_name", get_client_name(), reload_settings=True)
        self.set_setting("custom_client_name", get_client_name(), reload_settings=True)
        set_task_description(get_current_activity(), get_client_name(), get_saved_icon(self))

    def on_client_icon_reset(self, v):
        self.set_setting("custom_client_icon", "", reload_settings=True)
        set_task_description(get_current_activity(), self.get_setting("custom_client_name", get_client_name()), None)

    def on_create_shortcut(self, v):
        create_shortcut(
            self.get_setting("custom_client_name", get_client_name()),
            icon_bitmap=get_saved_icon(self)
        )

    def on_open_github(self, v):
        Browser.openUrl(get_current_activity(), Uri.parse(GITHUB_URL))

    def on_open_packit(self, v):
        Browser.openUrl(get_current_activity(), Uri.parse(PACKIT_URL))
    
    def create_settings(self) -> List[Any]:
        return [
            Header(text=get_str("client_name")),
            Input(
                key="custom_client_name",
                link_alias="custom_client_name",
                default=self.get_setting("custom_client_name", get_client_name()),
                text=get_str("custom_name"),
                subtext=get_str("enter_custom_client_name"),
                icon="menu_tag_rename",
                on_change=self.on_client_name_input_change,
            ),
            Text(
                link_alias="reset_custom_client_name",
                text=get_str("reset_to_default"),
                icon="msg_reset",
                red=True,
                on_click=self.on_client_name_reset,
            ),
            Header(text=get_str("client_icon")),
            Text(
                link_alias="custom_client_icon",
                text=get_str("select_custom_icon"),
                icon="msg_photos",
                on_click=pick_icon,
            ),
            Text(
                link_alias="reset_custom_client_icon",
                text=get_str("reset_to_default"),
                icon="msg_reset",
                red=True,
                on_click=self.on_client_icon_reset,
            ),
            Header(text=get_str("shortcut")),
            Text(
                link_alias="create_shortcut",
                text=get_str("create_shortcut"),
                icon="msg_home",
                on_click=self.on_create_shortcut,
                accent=True
            ),
            Divider(text=get_str("create_shortcut_info")),
            Header(text=get_str("info")),
            Text(
                link_alias="plugin_info",
                icon="msg_info",
                text=__name__ + " v" + __version__
            ),
            Text(
                link_alias="github",
                icon="msg_link",
                text="GitHub",
                on_click=self.on_open_github
            ),
            Text(
                link_alias="packit",
                icon="msg_link",
                text="PackIt",
                on_click=self.on_open_packit
            )
        ]
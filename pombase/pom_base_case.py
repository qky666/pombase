from __future__ import annotations
import typing
import os
import overrides
import selenium.webdriver.remote.webdriver as webdriver
import seleniumbase
import seleniumbase.config.settings as sb_settings
import seleniumbase.core.browser_launcher as browser_launcher
import seleniumbase.core.download_helper as download_helper
import seleniumbase.fixtures.constants as sb_constants
import seleniumbase.fixtures.page_utils as page_utils
import selenium.webdriver.common.desired_capabilities as desired_capabilities
import selenium.webdriver.ie.options as selenium_ie_options
from selenium.webdriver.common.by import By
import msedge.selenium_tools as edge_tools
# noinspection PyPackageRequirements
import src.testproject.classes as tp_classes
# noinspection PyPackageRequirements
import src.testproject.enums as tp_enums
# noinspection PyPackageRequirements
import src.testproject.enums.environmentvariable as environmentvariable


import pombase.webdriver as pb_webdriver
import pombase.config as pb_config
import pombase.constant as constants
import pombase.util as util
import pombase.web_node as web_node
import pombase.locator as locator
import pombase.types as types


def auth_user_pass(proxy_string: typing.Optional[str],
                   browser_name: str) -> tuple[bool, typing.Optional[str], typing.Optional[str]]:
    proxy_auth = False
    proxy_user = None
    proxy_pass = None
    if proxy_string:
        if "@" in proxy_string:
            # Format => username:password@hostname:port
            try:
                username_and_password = proxy_string.split("@")[0]
                proxy_string = proxy_string.split("@")[1]
                proxy_user = username_and_password.split(":")[0]
                proxy_pass = username_and_password.split(":")[1]
            except Exception:
                raise Exception(
                    "The format for using a proxy server with authentication "
                    'is: "username:password@hostname:port". If using a proxy '
                    'server without auth, the format is: "hostname:port".'
                )
            if browser_name != sb_constants.Browser.GOOGLE_CHROME and (
                    browser_name != sb_constants.Browser.EDGE
            ):
                raise Exception(
                    "Chrome or Edge is required when using a proxy server "
                    "that has authentication! (If using a proxy server "
                    "without auth, Chrome, Edge, or Firefox may be used.)"
                )
        proxy_string = browser_launcher.validate_proxy_string(proxy_string)
        if proxy_string and proxy_user and proxy_pass:
            proxy_auth = True
    return proxy_auth, proxy_user, proxy_pass


def recalculate_selector_by(selector: typing.Union[str, web_node.WebNode], by: str = None):
    if isinstance(selector, web_node.WebNode):
        return selector.locator.selector, selector.locator.by
    elif by is None:
        return selector, locator.infer_by_from_selector(selector)
    elif by == By.CSS_SELECTOR and locator.infer_by_from_selector(selector) == By.XPATH:
        return selector, By.XPATH
    else:
        return selector, by


class PomBaseCase(seleniumbase.BaseCase, overrides.EnforceOverrides):

    @overrides.overrides
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tp_project_name = None
        self.tp_job_name = None
        self.tp_test_name = None

    @property
    def pbconfig(self) -> pb_config.Config:
        return pb_config.Config()

    @overrides.overrides
    def get_new_driver(self,
                       browser=None,
                       headless=None,
                       locale_code=None,
                       protocol=None,
                       servername=None,
                       port=None,
                       proxy=None,
                       agent=None,
                       switch_to=True,
                       cap_file=None,
                       cap_string=None,
                       disable_csp=None,
                       enable_ws=None,
                       enable_sync=None,
                       use_auto_ext=None,
                       no_sandbox=None,
                       disable_gpu=None,
                       incognito=None,
                       guest_mode=None,
                       devtools=None,
                       remote_debug=None,
                       swiftshader=None,
                       block_images=None,
                       chromium_arg=None,
                       firefox_arg=None,
                       firefox_pref=None,
                       user_data_dir=None,
                       extension_zip=None,
                       extension_dir=None,
                       is_mobile=None,
                       d_width=None,
                       d_height=None,
                       d_p_r=None,
                       ):
        token = self.pbconfig.tp_dev_token
        if token is not None:
            self._BaseCase__check_scope()
            browser = util.first_not_none(browser, self.browser)
            browser_name = browser
            headless = util.first_not_none(headless, self.headless)
            locale_code = util.first_not_none(locale_code, self.locale_code)
            # protocol = util.first_not_none(protocol, self.protocol)
            servername = util.first_not_none(servername, self.servername)
            # port = util.first_not_none(port, self.port)
            # use_grid = False
            # if servername != "localhost":
            #     # Use Selenium Grid (Use "127.0.0.1" for localhost Grid)
            #     use_grid = True
            proxy_string = util.first_not_none(proxy, self.proxy_string)
            user_agent = util.first_not_none(agent, self.user_agent)
            disable_csp = util.first_not_none(disable_csp, self.disable_csp)
            enable_ws = util.first_not_none(enable_ws, self.enable_ws)
            enable_sync = util.first_not_none(enable_sync, self.enable_sync)
            use_auto_ext = util.first_not_none(use_auto_ext, self.use_auto_ext)
            no_sandbox = util.first_not_none(no_sandbox, self.no_sandbox)
            disable_gpu = util.first_not_none(disable_gpu, self.disable_gpu)
            incognito = util.first_not_none(incognito, self.incognito)
            guest_mode = util.first_not_none(guest_mode, self.guest_mode)
            devtools = util.first_not_none(devtools, self.devtools)
            remote_debug = util.first_not_none(remote_debug, self.remote_debug)
            swiftshader = util.first_not_none(swiftshader, self.swiftshader)
            block_images = util.first_not_none(block_images, self.block_images)
            chromium_arg = util.first_not_none(chromium_arg, self.chromium_arg)
            firefox_arg = util.first_not_none(firefox_arg, self.firefox_arg)
            firefox_pref = util.first_not_none(firefox_pref, self.firefox_pref)
            user_data_dir = util.first_not_none(user_data_dir, self.user_data_dir)
            extension_zip = util.first_not_none(extension_zip, self.extension_zip)
            extension_dir = util.first_not_none(extension_dir, self.extension_dir)
            # test_id = self.__get_test_id()
            # cap_file = util.first_not_none(cap_file, self.cap_file)
            # cap_string = util.first_not_none(cap_string, self.cap_string)
            is_mobile = util.first_not_none(is_mobile, self.mobile_emulator)
            mobile_emulator = is_mobile
            d_width = util.first_not_none(d_width, self._BaseCase__device_width)
            device_width = d_width
            d_height = util.first_not_none(d_height, self._BaseCase__device_height)
            device_height = d_height
            d_p_r = util.first_not_none(d_p_r, self._BaseCase__device_pixel_ratio)
            device_pixel_ratio = d_p_r

            proxy_auth, proxy_user, proxy_pass = auth_user_pass(proxy_string, browser_name)
            downloads_path = download_helper.get_downloads_folder()

            driver_class = constants.TP_DRIVER_CLASS[browser]
            driver_kwargs = {}
            if driver_class == pb_webdriver.Firefox:
                firefox_options = browser_launcher._set_firefox_options(
                    downloads_path=downloads_path,
                    headless=headless,
                    locale_code=locale_code,
                    proxy_string=proxy_string,
                    user_agent=user_agent,
                    disable_csp=disable_csp,
                    firefox_arg=firefox_arg,
                    firefox_pref=firefox_pref,
                )
                firefox_capabilities = desired_capabilities.DesiredCapabilities.FIREFOX.copy()
                if headless:
                    firefox_capabilities["moz:firefoxOptions"] = {
                        "args": ["-headless"]
                    }
                driver_kwargs["firefox_options"] = firefox_options
                driver_kwargs["desired_capabilities"] = firefox_capabilities
            elif driver_class == pb_webdriver.Ie:
                ie_options = selenium_ie_options.Options()
                ie_options.ignore_protected_mode_settings = True
                ie_options.ignore_zoom_level = True
                ie_options.require_window_focus = False
                ie_options.native_events = True
                ie_options.full_page_screenshot = True
                ie_options.persistent_hover = True
                ie_capabilities = ie_options.to_capabilities()
                driver_kwargs["capabilities"] = ie_capabilities
            elif driver_class == pb_webdriver.Edge:
                prefs = {
                    "download.default_directory": downloads_path,
                    "local_discovery.notifications_enabled": False,
                    "credentials_enable_service": False,
                    "download.prompt_for_download": False,
                    "download.directory_upgrade": True,
                    "safebrowsing.enabled": False,
                    "safebrowsing.disable_download_protection": True,
                    "default_content_setting_values.notifications": 0,
                    "default_content_settings.popups": 0,
                    "managed_default_content_settings.popups": 0,
                    "content_settings.exceptions.automatic_downloads.*.setting": 1,
                    "profile.password_manager_enabled": False,
                    "profile.default_content_setting_values.notifications": 0,
                    "profile.default_content_settings.popups": 0,
                    "profile.managed_default_content_settings.popups": 0,
                    "profile.default_content_setting_values.automatic_downloads": 1,
                }

                edge_options = edge_tools.EdgeOptions()
                edge_options.use_chromium = True
                if locale_code:
                    prefs["intl.accept_languages"] = locale_code
                if block_images:
                    prefs["profile.managed_default_content_settings.images"] = 2
                edge_options.add_experimental_option("prefs", prefs)
                edge_options.add_experimental_option("w3c", True)
                edge_options.add_argument(
                    "--disable-blink-features=AutomationControlled"
                )
                edge_options.add_experimental_option(
                    "useAutomationExtension", False
                )
                edge_options.add_experimental_option(
                    "excludeSwitches", ["enable-automation", "enable-logging"]
                )
                if guest_mode:
                    edge_options.add_argument("--guest")
                if headless:
                    edge_options.add_argument("--headless")
                if mobile_emulator:
                    emulator_settings = {}
                    device_metrics = {}
                    if (
                            type(device_width) is int
                            and type(device_height) is int
                            and type(device_pixel_ratio) is int
                    ):
                        device_metrics["width"] = device_width
                        device_metrics["height"] = device_height
                        device_metrics["pixelRatio"] = device_pixel_ratio
                    else:
                        device_metrics["width"] = 411
                        device_metrics["height"] = 731
                        device_metrics["pixelRatio"] = 3
                    emulator_settings["deviceMetrics"] = device_metrics
                    if user_agent:
                        emulator_settings["userAgent"] = user_agent
                    edge_options.add_experimental_option(
                        "mobileEmulation", emulator_settings
                    )
                    edge_options.add_argument("--enable-sync")
                if user_data_dir:
                    abs_path = os.path.abspath(user_data_dir)
                    edge_options.add_argument("user-data-dir=%s" % abs_path)
                if extension_zip:
                    # Can be a comma-separated list of .ZIP or .CRX files
                    extension_zip_list = extension_zip.split(",")
                    for extension_zip_item in extension_zip_list:
                        abs_path = os.path.abspath(extension_zip_item)
                        edge_options.add_extension(abs_path)
                if extension_dir:
                    # load-extension input can be a comma-separated list
                    abs_path = os.path.abspath(extension_dir)
                    edge_options.add_argument("--load-extension=%s" % abs_path)
                edge_options.add_argument("--disable-infobars")
                edge_options.add_argument("--disable-save-password-bubble")
                edge_options.add_argument("--disable-single-click-autofill")
                edge_options.add_argument("--disable-autofill-keyboard-accessory-view[8]")
                edge_options.add_argument("--disable-translate")
                if not enable_ws:
                    edge_options.add_argument("--disable-web-security")
                edge_options.add_argument("--homepage=about:blank")
                edge_options.add_argument("--dns-prefetch-disable")
                edge_options.add_argument("--dom-automation")
                edge_options.add_argument("--disable-hang-monitor")
                edge_options.add_argument("--disable-prompt-on-repost")
                if (sb_settings.DISABLE_CSP_ON_CHROME or disable_csp) and not headless:
                    # Headless Edge doesn't support extensions, which are required
                    # for disabling the Content Security Policy on Edge
                    edge_options = browser_launcher._add_chrome_disable_csp_extension(edge_options)
                    edge_options.add_argument("--enable-sync")
                if proxy_string:
                    if proxy_auth:
                        edge_options = browser_launcher._add_chrome_proxy_extension(
                            edge_options, proxy_string, proxy_user, proxy_pass
                        )
                    edge_options.add_argument("--proxy-server=%s" % proxy_string)
                edge_options.add_argument("--test-type")
                edge_options.add_argument("--log-level=3")
                edge_options.add_argument("--no-first-run")
                edge_options.add_argument("--ignore-certificate-errors")
                if devtools and not headless:
                    edge_options.add_argument("--auto-open-devtools-for-tabs")
                edge_options.add_argument("--allow-file-access-from-files")
                edge_options.add_argument("--allow-insecure-localhost")
                edge_options.add_argument("--allow-running-insecure-content")
                if user_agent:
                    edge_options.add_argument("--user-agent=%s" % user_agent)
                edge_options.add_argument("--no-sandbox")
                if remote_debug:
                    # To access the Remote Debugger, go to: http://localhost:9222
                    # while a Chromium driver is running.
                    # Info: https://chromedevtools.github.io/devtools-protocol/
                    edge_options.add_argument("--remote-debugging-port=9222")
                if swiftshader:
                    edge_options.add_argument("--use-gl=swiftshader")
                else:
                    edge_options.add_argument("--disable-gpu")
                if chromium_arg:
                    # Can be a comma-separated list of Chromium args
                    chromium_arg_list = chromium_arg.split(",")
                    for chromium_arg_item in chromium_arg_list:
                        chromium_arg_item = chromium_arg_item.strip()
                        if not chromium_arg_item.startswith("--"):
                            if chromium_arg_item.startswith("-"):
                                chromium_arg_item = "-" + chromium_arg_item
                            else:
                                chromium_arg_item = "--" + chromium_arg_item
                        if len(chromium_arg_item) >= 3:
                            edge_options.add_argument(chromium_arg_item)
                capabilities = edge_options.to_capabilities()
                capabilities["platform"] = ""
                driver_kwargs["capabilities"] = capabilities
            elif driver_class == pb_webdriver.Safari:
                safari_capabilities = browser_launcher._set_safari_capabilities()
                driver_kwargs["desired_capabilities"] = safari_capabilities
            elif driver_class == pb_webdriver.Chrome:
                if user_data_dir and len(user_data_dir) < 3:
                    raise Exception(
                        "Name length of Chrome's User Data Directory must be >= 3."
                    )
                chrome_options = browser_launcher._set_chrome_options(
                    browser_name=sb_constants.Browser.GOOGLE_CHROME,
                    downloads_path=downloads_path,
                    headless=headless,
                    locale_code=locale_code,
                    proxy_string=proxy_string,
                    proxy_auth=proxy_auth,
                    proxy_user=proxy_user,
                    proxy_pass=proxy_pass,
                    user_agent=user_agent,
                    disable_csp=disable_csp,
                    enable_ws=enable_ws,
                    enable_sync=enable_sync,
                    use_auto_ext=use_auto_ext,
                    no_sandbox=no_sandbox,
                    disable_gpu=disable_gpu,
                    incognito=incognito,
                    guest_mode=guest_mode,
                    devtools=devtools,
                    remote_debug=remote_debug,
                    swiftshader=swiftshader,
                    block_images=block_images,
                    chromium_arg=chromium_arg,
                    user_data_dir=user_data_dir,
                    extension_zip=extension_zip,
                    extension_dir=extension_dir,
                    servername=servername,
                    mobile_emulator=is_mobile,
                    device_width=d_width,
                    device_height=d_height,
                    device_pixel_ratio=d_p_r,
                )
                driver_kwargs["chrome_options"] = chrome_options

            if self.tp_test_name is not None:
                os.environ[environmentvariable.EnvironmentVariable.TP_TEST_NAME.value] = self.tp_test_name
            new_driver = driver_class(
                token=token,
                project_name=util.first_not_none(self.tp_project_name, self.pbconfig.tp_project_name),
                job_name=util.first_not_none(self.tp_job_name, self.pbconfig.tp_job_name),
                agent_url=self.pbconfig.tp_agent_url,
                disable_reports=self.pbconfig.tp_disable_auto_reporting,
                report_type=self.pbconfig.tp_report_type,
                report_name=self.pbconfig.tp_report_name,
                report_path=self.pbconfig.tp_report_path,
                **driver_kwargs,
            )
            self._handle_new_driver(new_driver, browser_name, switch_to)
            return new_driver
        else:
            return super().get_new_driver(browser,
                                          headless,
                                          locale_code,
                                          protocol,
                                          servername,
                                          port,
                                          proxy,
                                          agent,
                                          switch_to,
                                          cap_file,
                                          cap_string,
                                          disable_csp,
                                          enable_ws,
                                          enable_sync,
                                          use_auto_ext,
                                          no_sandbox,
                                          disable_gpu,
                                          incognito,
                                          guest_mode,
                                          devtools,
                                          remote_debug,
                                          swiftshader,
                                          block_images,
                                          chromium_arg,
                                          firefox_arg,
                                          firefox_pref,
                                          user_data_dir,
                                          extension_zip,
                                          extension_dir,
                                          is_mobile,
                                          d_width,
                                          d_height,
                                          d_p_r, )

    def _handle_new_driver(self, new_driver: webdriver.WebDriver, browser_name: str, switch_to: bool) -> None:
        self._drivers_list.append(new_driver)
        self._BaseCase__driver_browser_map[new_driver] = browser_name
        if switch_to:
            self.driver: webdriver.WebDriver = new_driver
            self.browser = browser_name
            if self.headless:
                # Make sure the invisible browser window is big enough
                width = sb_settings.HEADLESS_START_WIDTH
                height = sb_settings.HEADLESS_START_HEIGHT
                # noinspection PyBroadException
                try:
                    self.driver.set_window_size(width, height)
                    self.wait_for_ready_state_complete()
                except Exception:
                    # This shouldn't fail, but in case it does,
                    # get safely through setUp() so that
                    # WebDrivers can get closed during tearDown().
                    pass
            else:
                if self.browser == "chrome" or self.browser == "edge":
                    width = sb_settings.CHROME_START_WIDTH
                    height = sb_settings.CHROME_START_HEIGHT
                    # noinspection PyBroadException
                    try:
                        if self.maximize_option:
                            self.driver.maximize_window()
                        else:
                            self.driver.set_window_size(width, height)
                        self.wait_for_ready_state_complete()
                    except Exception:
                        pass  # Keep existing browser resolution
                elif self.browser == "firefox":
                    width = sb_settings.CHROME_START_WIDTH
                    # noinspection PyBroadException
                    try:
                        if self.maximize_option:
                            self.driver.maximize_window()
                        else:
                            self.driver.set_window_size(width, 720)
                        self.wait_for_ready_state_complete()
                    except Exception:
                        pass  # Keep existing browser resolution
                elif self.browser == "safari":
                    width = sb_settings.CHROME_START_WIDTH
                    if self.maximize_option:
                        # noinspection PyBroadException
                        try:
                            self.driver.maximize_window()
                            self.wait_for_ready_state_complete()
                        except Exception:
                            pass  # Keep existing browser resolution
                    else:
                        # noinspection PyBroadException
                        try:
                            self.driver.set_window_rect(10, 30, width, 630)
                        except Exception:
                            pass
                # elif self.browser == "opera":
                #     width = sbsettings.CHROME_START_WIDTH
                #     if self.maximize_option:
                #         # noinspection PyBroadException
                #         try:
                #             self.driver.maximize_window()
                #             self.wait_for_ready_state_complete()
                #         except Exception:
                #             pass  # Keep existing browser resolution
                #     else:
                #         # noinspection PyBroadException
                #         try:
                #             self.driver.set_window_rect(10, 30, width, 700)
                #         except Exception:
                #             pass
            if self.start_page and len(self.start_page) >= 4:
                if page_utils.is_valid_url(self.start_page):
                    self.open(self.start_page)
                else:
                    new_start_page = "http://" + self.start_page
                    if page_utils.is_valid_url(new_start_page):
                        self.open(new_start_page)

            # Apply default settings
            step_settings = tp_classes.StepSettings(
                timeout=self.pbconfig.tp_default_timeout,
                sleep_time=self.pbconfig.tp_default_sleep_time,
                sleep_timing_type=self.pbconfig.tp_default_sleep_timing_type,
                screenshot_condition=self.pbconfig.tp_default_take_screenshot_condition_type,
            )
            previous_settings = new_driver.command_executor.settings
            # If inherit take the previous step settings.
            if step_settings.sleep_timing_type \
                    and step_settings.sleep_timing_type is tp_enums.SleepTimingType.Inherit:
                step_settings.sleep_timing_type = previous_settings.sleep_timing_type
            if step_settings.screenshot_condition \
                    and step_settings.screenshot_condition is tp_enums.TakeScreenshotConditionType.Inherit:
                step_settings.screenshot_condition = previous_settings.screenshot_condition
            new_driver.command_executor.settings = step_settings

    ######################
    # New utility methods
    ######################

    def count(self, selector: typing.Union[str, web_node.WebNode], by: str = None) -> int:
        node = web_node.node_from(selector, by)
        if node.ignore_invisible is True:
            return len(self.find_visible_elements(node))
        else:
            return len(self.find_elements(node))

    def is_iframe(self,
                  selector: typing.Union[str, web_node.WebNode],
                  by: str = None,
                  timeout: types.Number = None) -> bool:
        selector, by = recalculate_selector_by(selector, by)
        element = self.find_element(selector, by, timeout)
        if element is None:
            return False
        tag_name = element.tag_name
        if isinstance(tag_name, str) and util.caseless_equal(tag_name, "iframe"):
            return True
        else:
            return False

    #######################
    # SeleniumBase actions
    #######################

    @overrides.overrides
    def click(self, selector, by=By.CSS_SELECTOR, timeout=None, delay=0):
        selector, by = recalculate_selector_by(selector, by)
        super().click(selector, by, timeout, delay)

    @overrides.overrides
    def slow_click(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        super().slow_click(selector, by, timeout)

    @overrides.overrides
    def double_click(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().double_click(selector, by, timeout)

    @overrides.overrides
    def click_chain(self, selectors_list, by=By.CSS_SELECTOR, timeout=None, spacing=0):
        if isinstance(selectors_list, web_node.WebNode):
            selectors_list, by = [selectors_list.locator.selector], selectors_list.locator.by
        super().click_chain(selectors_list, by, timeout, spacing)

    @overrides.overrides
    def update_text(self, selector, text, by=By.CSS_SELECTOR, timeout=None, retry=False):
        selector, by = recalculate_selector_by(selector, by)
        super().update_text(selector, text, by, timeout, retry)

    @overrides.overrides
    def add_text(self, selector, text, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        super().add_text(selector, text, by, timeout)

    @overrides.overrides
    def type(self, selector, text, by=By.CSS_SELECTOR, timeout=None, retry=False):
        selector, by = recalculate_selector_by(selector, by)
        super().type(selector, text, by, timeout, retry)

    @overrides.overrides
    def submit(self, selector, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        super().submit(selector, by)

    @overrides.overrides
    def clear(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        super().clear(selector, by, timeout)

    @overrides.overrides
    def focus(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        super().focus(selector, by, timeout)

    @overrides.overrides
    def is_element_present(self, selector, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        return super().is_element_present(selector, by)

    @overrides.overrides
    def is_element_visible(self, selector, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        return super().is_element_visible(selector, by)

    @overrides.overrides
    def is_element_enabled(self, selector, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        return super().is_element_enabled(selector, by)

    @overrides.overrides
    def is_text_visible(self, text, selector="html", by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        return super().is_text_visible(text, selector, by)

    @overrides.overrides
    def get_text(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().get_text(selector, by, timeout)

    @overrides.overrides
    def get_attribute(self, selector, attribute, by=By.CSS_SELECTOR, timeout=None, hard_fail=True):
        selector, by = recalculate_selector_by(selector, by)
        return super().get_attribute(selector, attribute, by, timeout, hard_fail)

    @overrides.overrides
    def set_attribute(self, selector, attribute, value, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        super().set_attribute(selector, attribute, value, by, timeout)

    @overrides.overrides
    def set_attributes(self, selector, attribute, value, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        super().set_attributes(selector, attribute, value, by)

    @overrides.overrides
    def set_attribute_all(self, selector, attribute, value, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        super().set_attribute_all(selector, attribute, value, by)

    @overrides.overrides
    def remove_attribute(self, selector, attribute, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        super().remove_attribute(selector, attribute, by, timeout)

    @overrides.overrides
    def remove_attributes(self, selector, attribute, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        super().remove_attributes(selector, attribute, by)

    @overrides.overrides
    def get_property_value(self, selector, property, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().get_property_value(selector, property, by, timeout)

    @overrides.overrides
    def get_image_url(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().get_image_url(selector, by, timeout)

    @overrides.overrides
    def find_elements(self, selector, by=By.CSS_SELECTOR, limit=0):
        selector, by = recalculate_selector_by(selector, by)
        return super().find_elements(selector, by, limit)

    @overrides.overrides
    def find_visible_elements(self, selector, by=By.CSS_SELECTOR, limit=0):
        selector, by = recalculate_selector_by(selector, by)
        return super().find_visible_elements(selector, by, limit)

    @overrides.overrides
    def click_visible_elements(self, selector, by=By.CSS_SELECTOR, limit=0, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        super().click_visible_elements(selector, by, limit, timeout)

    @overrides.overrides
    def click_nth_visible_element(self, selector, number, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().click_nth_visible_element(selector, number, by, timeout)

    @overrides.overrides
    def click_if_visible(self, selector, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        super().click_if_visible(selector, by)

    @overrides.overrides
    def is_checked(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().is_checked(selector, by, timeout)

    @overrides.overrides
    def is_selected(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().is_selected(selector, by, timeout)

    @overrides.overrides
    def check_if_unchecked(self, selector, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        super().check_if_unchecked(selector, by)

    @overrides.overrides
    def select_if_unselected(self, selector, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        super().select_if_unselected(selector, by)

    @overrides.overrides
    def uncheck_if_checked(self, selector, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        super().uncheck_if_checked(selector, by)

    @overrides.overrides
    def unselect_if_selected(self, selector, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        super().unselect_if_selected(selector, by)

    @overrides.overrides
    def is_element_in_an_iframe(self, selector, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        return super().is_element_in_an_iframe(selector, by)

    @overrides.overrides
    def switch_to_frame_of_element(self, selector, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        return super().switch_to_frame_of_element(selector, by)

    @overrides.overrides
    def hover_on_element(self, selector, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        super().hover_on_element(selector, by)

    @overrides.overrides
    def hover_and_click(self, hover_selector, click_selector, hover_by=By.CSS_SELECTOR, click_by=By.CSS_SELECTOR,
                        timeout=None):
        hover_selector, hover_by = recalculate_selector_by(hover_selector, hover_by)
        click_selector, click_by = recalculate_selector_by(click_selector, click_by)
        return super().hover_and_click(hover_selector, click_selector, hover_by, click_by, timeout)

    @overrides.overrides
    def hover_and_double_click(self, hover_selector, click_selector, hover_by=By.CSS_SELECTOR, click_by=By.CSS_SELECTOR,
                               timeout=None):
        hover_selector, hover_by = recalculate_selector_by(hover_selector, hover_by)
        click_selector, click_by = recalculate_selector_by(click_selector, click_by)
        return super().hover_and_double_click(hover_selector, click_selector, hover_by, click_by, timeout)

    @overrides.overrides
    def drag_and_drop(self, drag_selector, drop_selector, drag_by=By.CSS_SELECTOR, drop_by=By.CSS_SELECTOR,
                      timeout=None):
        drag_selector, drag_by = recalculate_selector_by(drag_selector, drag_by)
        drop_selector, drop_by = recalculate_selector_by(drop_selector, drop_by)
        return super().drag_and_drop(drag_selector, drop_selector, drag_by, drop_by, timeout)

    @overrides.overrides
    def drag_and_drop_with_offset(self, selector, x, y, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().drag_and_drop_with_offset(selector, x, y, by, timeout)

    @overrides.overrides
    def select_option_by_text(self, dropdown_selector, option, dropdown_by=By.CSS_SELECTOR, timeout=None):
        dropdown_selector, dropdown_by = recalculate_selector_by(dropdown_selector, dropdown_by)
        super().select_option_by_text(dropdown_selector, option, dropdown_by, timeout)

    @overrides.overrides
    def select_option_by_index(self, dropdown_selector, option, dropdown_by=By.CSS_SELECTOR, timeout=None):
        dropdown_selector, dropdown_by = recalculate_selector_by(dropdown_selector, dropdown_by)
        super().select_option_by_index(dropdown_selector, option, dropdown_by, timeout)

    @overrides.overrides
    def select_option_by_value(self, dropdown_selector, option, dropdown_by=By.CSS_SELECTOR, timeout=None):
        dropdown_selector, dropdown_by = recalculate_selector_by(dropdown_selector, dropdown_by)
        super().select_option_by_value(dropdown_selector, option, dropdown_by, timeout)

    @overrides.overrides
    def bring_to_front(self, selector, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        super().bring_to_front(selector, by)

    @overrides.overrides
    def highlight_click(self, selector, by=By.CSS_SELECTOR, loops=3, scroll=True):
        selector, by = recalculate_selector_by(selector, by)
        super().highlight_click(selector, by, loops, scroll)

    @overrides.overrides
    def highlight_update_text(self, selector, text, by=By.CSS_SELECTOR, loops=3, scroll=True):
        selector, by = recalculate_selector_by(selector, by)
        super().highlight_update_text(selector, text, by, loops, scroll)

    @overrides.overrides
    def highlight(self, selector, by=By.CSS_SELECTOR, loops=None, scroll=True):
        selector, by = recalculate_selector_by(selector, by)
        super().highlight(selector, by, loops, scroll)

    @overrides.overrides
    def press_up_arrow(self, selector="html", times=1, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        super().press_up_arrow(selector, times, by)

    @overrides.overrides
    def press_down_arrow(self, selector="html", times=1, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        super().press_down_arrow(selector, times, by)

    @overrides.overrides
    def press_left_arrow(self, selector="html", times=1, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        super().press_left_arrow(selector, times, by)

    @overrides.overrides
    def press_right_arrow(self, selector="html", times=1, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        super().press_right_arrow(selector, times, by)

    @overrides.overrides
    def scroll_to(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        super().scroll_to(selector, by, timeout)

    @overrides.overrides
    def scroll_to_element(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        super().scroll_to_element(selector, by, timeout)

    @overrides.overrides
    def slow_scroll_to(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        super().slow_scroll_to(selector, by, timeout)

    @overrides.overrides
    def slow_scroll_to_element(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        super().slow_scroll_to_element(selector, by, timeout)

    @overrides.overrides
    def js_click(self, selector, by=By.CSS_SELECTOR, all_matches=False):
        selector, by = recalculate_selector_by(selector, by)
        super().js_click(selector, by, all_matches)

    @overrides.overrides
    def js_click_all(self, selector, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        super().js_click_all(selector, by)

    @overrides.overrides
    def jquery_click(self, selector, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        super().jquery_click(selector, by)

    @overrides.overrides
    def jquery_click_all(self, selector, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        super().jquery_click_all(selector, by)

    @overrides.overrides
    def hide_element(self, selector, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        super().hide_element(selector, by)

    @overrides.overrides
    def hide_elements(self, selector, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        super().hide_elements(selector, by)

    @overrides.overrides
    def show_element(self, selector, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        super().show_element(selector, by)

    @overrides.overrides
    def show_elements(self, selector, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        super().show_elements(selector, by)

    @overrides.overrides
    def remove_element(self, selector, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        super().remove_element(selector, by)

    @overrides.overrides
    def remove_elements(self, selector, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        super().remove_elements(selector, by)

    @overrides.overrides
    def choose_file(self, selector, file_path, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().choose_file(selector, file_path, by, timeout)

    @overrides.overrides
    def set_value(self, selector, text, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        super().set_value(selector, text, by, timeout)

    @overrides.overrides
    def js_update_text(self, selector, text, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        super().js_update_text(selector, text, by, timeout)

    @overrides.overrides
    def js_type(self, selector, text, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        super().js_type(selector, text, by, timeout)

    @overrides.overrides
    def set_text(self, selector, text, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        super().set_text(selector, text, by, timeout)

    @overrides.overrides
    def jquery_update_text(self, selector, text, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        super().jquery_update_text(selector, text, by, timeout)

    @overrides.overrides
    def input(self, selector, text, by=By.CSS_SELECTOR, timeout=None, retry=False):
        selector, by = recalculate_selector_by(selector, by)
        super().input(selector, text, by, timeout, retry)

    @overrides.overrides
    def fill(self, selector, text, by=By.CSS_SELECTOR, timeout=None, retry=False):
        selector, by = recalculate_selector_by(selector, by)
        super().fill(selector, text, by, timeout, retry)

    @overrides.overrides
    def write(self, selector, text, by=By.CSS_SELECTOR, timeout=None, retry=False):
        selector, by = recalculate_selector_by(selector, by)
        super().write(selector, text, by, timeout, retry)

    @overrides.overrides
    def send_keys(self, selector, text, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        super().send_keys(selector, text, by, timeout)

    @overrides.overrides
    def wait_for_element_visible(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().wait_for_element_visible(selector, by, timeout)

    @overrides.overrides
    def wait_for_element_not_present(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().wait_for_element_not_present(selector, by, timeout)

    @overrides.overrides
    def assert_element_not_present(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().assert_element_not_present(selector, by, timeout)

    @overrides.overrides
    def post_message_and_highlight(self, message, selector, by=By.CSS_SELECTOR):
        selector, by = recalculate_selector_by(selector, by)
        super().post_message_and_highlight(message, selector, by)

    @overrides.overrides
    def wait_for_element_present(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().wait_for_element_present(selector, by, timeout)

    @overrides.overrides
    def wait_for_element(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().wait_for_element(selector, by, timeout)

    @overrides.overrides
    def get_element(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().get_element(selector, by, timeout)

    @overrides.overrides
    def assert_element_present(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().assert_element_present(selector, by, timeout)

    @overrides.overrides
    def find_element(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().find_element(selector, by, timeout)

    @overrides.overrides
    def assert_element(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().assert_element(selector, by, timeout)

    @overrides.overrides
    def assert_element_visible(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().assert_element_visible(selector, by, timeout)

    @overrides.overrides
    def assert_elements(self, *args, **kwargs):
        new_args = []
        for arg in args:
            if isinstance(arg, web_node.WebNode):
                new_args.append(arg.locator.selector)
                if "by" in kwargs:
                    assert kwargs["by"] == arg.locator.by, \
                        f"Incorrect 'by' in assert_elements kwargs. Found: {kwargs['by']}. Expected: {arg.locator.by}"
                else:
                    kwargs["by"] = arg.locator.by
            else:
                new_args.append(arg)
        return super().assert_elements(*new_args, **kwargs)

    @overrides.overrides
    def wait_for_text_visible(self, text, selector="html", by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().wait_for_text_visible(text, selector, by, timeout)

    @overrides.overrides
    def wait_for_exact_text_visible(self, text, selector="html", by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().wait_for_exact_text_visible(text, selector, by, timeout)

    @overrides.overrides
    def wait_for_text(self, text, selector="html", by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().wait_for_text(text, selector, by, timeout)

    @overrides.overrides
    def find_text(self, text, selector="html", by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().find_text(text, selector, by, timeout)

    @overrides.overrides
    def assert_text_visible(self, text, selector="html", by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().assert_text_visible(text, selector, by, timeout)

    @overrides.overrides
    def assert_text(self, text, selector="html", by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().assert_text(text, selector, by, timeout)

    @overrides.overrides
    def assert_exact_text(self, text, selector="html", by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().assert_exact_text(text, selector, by, timeout)

    @overrides.overrides
    def wait_for_element_absent(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().wait_for_element_absent(selector, by, timeout)

    @overrides.overrides
    def assert_element_absent(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().assert_element_absent(selector, by, timeout)

    @overrides.overrides
    def wait_for_element_not_visible(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().wait_for_element_not_visible(selector, by, timeout)

    @overrides.overrides
    def assert_element_not_visible(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().assert_element_not_visible(selector, by, timeout)

    @overrides.overrides
    def wait_for_text_not_visible(self, text, selector="html", by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().wait_for_text_not_visible(text, selector, by, timeout)

    @overrides.overrides
    def assert_text_not_visible(self, text, selector="html", by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().assert_text_not_visible(text, selector, by, timeout)

    @overrides.overrides
    def deferred_assert_element(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().deferred_assert_element(selector, by, timeout)

    @overrides.overrides
    def deferred_assert_text(self, text, selector="html", by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().deferred_assert_text(text, selector, by, timeout)

    @overrides.overrides
    def delayed_assert_element(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().delayed_assert_element(selector, by, timeout)

    @overrides.overrides
    def delayed_assert_text(self, text, selector="html", by=By.CSS_SELECTOR, timeout=None):
        selector, by = recalculate_selector_by(selector, by)
        return super().delayed_assert_text(text, selector, by, timeout)

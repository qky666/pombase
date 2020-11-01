from __future__ import annotations

import typing
import regex

from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.remote.webdriver import WebDriver

from . import web_node


class WebElementUtil:
    CANONICAL_XPATH = "pom_canonical_xpath"
    CANONICAL_CSS = "pom_canonical_css"
    WEB_NODE = "pom_web_node"

    @staticmethod
    def web_element_match_text_pattern(web_element: WebElement,
                                       text_pattern: str,
                                       use_regexp_in_text_pattern: bool,
                                       ignore_case_in_text_pattern: bool) -> typing.Optional[bool]:
        if text_pattern is None:
            return True
        else:
            # Convert to regular expression
            if use_regexp_in_text_pattern is False:
                # "?" -> ".", "*" -> ".*"
                # Except "\?" or "\*"
                parts = text_pattern.split("*")
                pattern = ""
                for part in parts[:-1]:
                    if part[-1] == "\\":
                        pattern = pattern + part + "*"
                    else:
                        pattern = pattern + part + ".*"
                pattern = pattern + parts[-1]
                parts = pattern.split("?")
                pattern = ""
                for part in parts[:-1]:
                    if part[-1] == "\\":
                        pattern = pattern + part + "?"
                    else:
                        pattern = pattern + part + "."
                pattern = pattern + parts[-1]
                lines = pattern.splitlines()
                pattern = "".join([f"^{line}$" for line in lines])
            else:
                pattern = text_pattern
            try:
                text = web_element.text
            except StaleElementReferenceException:
                return None
            flags = regex.MULTILINE | regex.LOCALE | regex.DOTALL | regex.UNICODE
            if ignore_case_in_text_pattern is True:
                flags = flags | regex.IGNORECASE
            if regex.search(pattern, text, flags) is None:
                return False
            else:
                return True

    @staticmethod
    def canonical_xpath_for_web_element(web_element: WebElement, driver: WebDriver) -> typing.Optional[str]:
        jscript = """
        function createXPathFromElement(elm) { 
            var allNodes = document.getElementsByTagName('*'); 
            for (var segs = []; elm && elm.nodeType == 1; elm = elm.parentNode) 
            { 
                if (elm.hasAttribute('id')) { 
                    var uniqueIdCount = 0; 
                    for (var n=0;n < allNodes.length;n++) { 
                        if (allNodes[n].hasAttribute('id') && allNodes[n].id == elm.id) uniqueIdCount++; 
                        if (uniqueIdCount > 1) break; 
                    }; 
                    if ( uniqueIdCount == 1) { 
                        segs.unshift('id("' + elm.getAttribute('id') + '")'); 
                        return segs.join('/'); 
                    } else { 
                        segs.unshift(elm.localName.toLowerCase() + '[@id="' + elm.getAttribute('id') + '"]'); 
                    } 
                } else { 
                    for (i = 1, sib = elm.previousSibling; sib; sib = sib.previousSibling) { 
                        if (sib.localName == elm.localName)  i++; }; 
                        segs.unshift(elm.localName.toLowerCase() + '[' + i + ']'); 
                }; 
            }; 
            return segs.length ? '/' + segs.join('/') : null; 
        }; 
        return createXPathFromElement(arguments[0]);
        """
        try:
            xpath = driver.execute_script(jscript, web_element)
        except StaleElementReferenceException:
            return None
        xpath_element = driver.find_element_by_xpath(xpath)
        if web_element.id != xpath_element.id:
            return None
        return xpath

    @staticmethod
    def canonical_css_for_web_element(web_element: WebElement, driver: WebDriver) -> typing.Optional[str]:
        jscript = """
            function createCSSFromElement(elm) { 
                var allNodes = document.getElementsByTagName('*'); 
                for (var segs = []; elm && elm.nodeType == 1; elm = elm.parentNode) 
                { 
                    if (elm.hasAttribute('id')) { 
                        var uniqueIdCount = 0; 
                        for (var n=0;n < allNodes.length;n++) { 
                            if (allNodes[n].hasAttribute('id') && allNodes[n].id == elm.id) uniqueIdCount++; 
                            if (uniqueIdCount > 1) break; 
                        }; 
                        if ( uniqueIdCount == 1) { 
                            segs.unshift('#' + elm.getAttribute('id')); 
                            return segs.join('>'); 
                        } else { 
                            segs.unshift(elm.localName.toLowerCase() + '#' + elm.getAttribute('id')); 
                        } 
                    } else { 
                        for (i = 1, sib = elm.previousSibling; sib; sib = sib.previousSibling) { 
                            if (sib.localName == elm.localName)  i++; }; 
                            segs.unshift(elm.localName.toLowerCase() + ':nth-child(' + i + ')'); 
                    }; 
                }; 
                return segs.length ? segs.join('>') : null; 
            }; 
            return createCSSFromElement(arguments[0]);
            """
        try:
            css = driver.execute_script(jscript, web_element)
        except StaleElementReferenceException:
            return None
        css_element = driver.find_element_by_css_selector(css)
        if web_element.id != css_element.id:
            return None
        return css

    @staticmethod
    def attach_canonical_xpath_css_and_node_to_web_element(
            web_element: WebElement,
            node: web_node.WebNode = None,
    ) -> typing.Optional[WebElement]:

        xpath = WebElementUtil.canonical_xpath_for_web_element(web_element, node.pom_base_case.driver)
        if xpath is None:
            return None
        setattr(web_element, WebElementUtil.CANONICAL_XPATH, xpath)
        css = WebElementUtil.canonical_css_for_web_element(web_element, node.pom_base_case.driver)
        if css is None:
            return None
        setattr(web_element, WebElementUtil.CANONICAL_CSS, css)
        if node is not None:
            setattr(web_element, WebElementUtil.WEB_NODE, node)
        return web_element

    @staticmethod
    def validate_web_element(web_element: WebElement) -> bool:
        try:
            tag = web_element.tag_name
            if tag is None:
                # Just to make PyCharm not complaining
                return False
        except StaleElementReferenceException:
            return False
        xpath = getattr(web_element, WebElementUtil.CANONICAL_XPATH)
        css = getattr(web_element, WebElementUtil.CANONICAL_CSS)
        node = getattr(web_element, WebElementUtil.WEB_NODE)
        driver = node.pom_base_case.driver
        xpath_element = driver.find_element_by_xpath(xpath)
        css_element = driver.find_element_by_css_selector(css)
        if web_element.id != xpath_element.id or web_element.id != css_element.id:
            return False
        else:
            return True

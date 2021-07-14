from __future__ import annotations

import typing
import inflection
import os

from pombase.prev_version import web_node


class Action:

    def __init__(self, *args, **kwargs):
        self.node: typing.Optional[web_node.WebNode] = None
        self.method: str = inflection.underscore(type(self).__name__)
        self.args: tuple = args
        self.kwargs: dict = kwargs

    def run(self) -> typing.Any:
        return getattr(self.node, self.method)(*self.args, **self.kwargs)


class Click(Action):

    def __init__(self, timeout: typing.Union[int, float] = None, delay: int = 0):
        super().__init__(timeout, delay)


class SlowClick(Action):

    def __init__(self, timeout: typing.Union[int, float] = None):
        super().__init__(timeout)


class DoubleClick(Action):

    def __init__(self, timeout: typing.Union[int, float] = None):
        super().__init__(timeout)


class ClickChain(Action):

    def __init__(self, timeout: typing.Union[int, float] = None, spacing: int = 0):
        super().__init__(timeout, spacing)


class Type(Action):

    def __init__(self, text: str, timeout: typing.Union[int, float] = None, retry: bool = True):
        super().__init__(text, timeout, retry)


class AddText(Action):

    def __init__(self, text: typing.Union[str, int, float], timeout: typing.Union[int, float] = None):
        super().__init__(text, timeout)


class Submit(Action):

    def __init__(self):
        super().__init__()


class Clear(Action):

    def __init__(self, timeout: typing.Union[int, float] = None):
        super().__init__(timeout)


class IsTextVisible(Action):

    def __init__(self, text: str):
        super().__init__(text)


class GetText(Action):

    def __init__(self, timeout: typing.Union[int, float] = None):
        super().__init__(timeout)


class GetAttribute(Action):

    def __init__(self,
                 attribute: str,
                 timeout: typing.Union[int, float] = None,
                 hard_fail: bool = True):
        super().__init__(attribute, timeout, hard_fail)


class SetAttribute(Action):

    def __init__(self, attribute: str, value: typing.Any, timeout: typing.Union[int, float] = None):
        super().__init__(attribute, value, timeout)


class SetAttributes(Action):

    def __init__(self, attribute: str, value: typing.Any):
        super().__init__(attribute, value)


class RemoveAttribute(Action):

    def __init__(self, attribute: str, timeout: typing.Union[int, float] = None):
        super().__init__(attribute, timeout)


class RemoveAttributes(Action):

    def __init__(self, attribute: str):
        super().__init__(attribute)


class GetPropertyValue(Action):

    # noinspection PyShadowingBuiltins
    def __init__(self, property: str, timeout: typing.Union[int, float] = None):
        super().__init__(property, timeout)


class GetImageUrl(Action):

    def __init__(self, timeout: typing.Union[int, float] = None):
        super().__init__(timeout)


class ClickVisibleElements(Action):

    def __init__(self, limit: int = 0, timeout: typing.Union[int, float] = None):
        super().__init__(limit, timeout)


class ClickNthVisibleElement(Action):

    def __init__(self, number: int, timeout: typing.Union[int, float] = None):
        super().__init__(number, timeout)


class ClickIfVisible(Action):

    def __init__(self):
        super().__init__()


class IsSelected(Action):

    def __init__(self, timeout: typing.Union[int, float] = None):
        super().__init__(timeout)


class SelectIfUnselected(Action):

    def __init__(self):
        super().__init__()


class UnSelectIfSelected(Action):

    def __init__(self):
        super().__init__()


class IsElementInAnIframe(Action):

    def __init__(self):
        super().__init__()


class SwitchToFrameOfElement(Action):

    def __init__(self):
        super().__init__()


class HoverOnElement(Action):

    def __init__(self):
        super().__init__()


class HoverAndClick(Action):

    def __init__(self, click_node: typing.Union[str, web_node.WebNode], timeout: typing.Union[int, float] = None):
        super().__init__(click_node, timeout)


class HoverAndDoubleClick(Action):

    def __init__(self, click_node: typing.Union[str, web_node.WebNode], timeout: typing.Union[int, float] = None):
        super().__init__(click_node, timeout)


class DragAndDrop(Action):

    def __init__(self, drop_node: typing.Union[str, web_node.WebNode], timeout: typing.Union[int, float] = None):
        super().__init__(drop_node, timeout)


class SelectOptionByText(Action):

    def __init__(self, option: str, timeout: typing.Union[int, float] = None):
        super().__init__(option, timeout)


class SelectOptionByIndex(Action):

    def __init__(self, option: int, timeout: typing.Union[int, float] = None):
        super().__init__(option, timeout)


class SelectOptionByValue(Action):

    def __init__(self, option: str, timeout: typing.Union[int, float] = None):
        super().__init__(option, timeout)


class SwitchToFrame(Action):

    def __init__(self, timeout: typing.Union[int, float] = None):
        super().__init__(timeout)


class BringToFront(Action):

    def __init__(self):
        super().__init__()


class HighlightClick(Action):

    def __init__(self, loops: int = 3, scroll: bool = True):
        super().__init__(loops, scroll)


class HighlightUpdateText(Action):

    def __init__(self, text: str, loops: int = 3, scroll: bool = True):
        super().__init__(text, loops, scroll)


class Highlight(Action):

    def __init__(self, loops: int = 4, scroll: bool = True):
        super().__init__(loops, scroll)


class PressUpArrow(Action):

    def __init__(self, times: int = 1):
        super().__init__(times)


class PressDownArrow(Action):

    def __init__(self, times: int = 1):
        super().__init__(times)


class PressLeftArrow(Action):

    def __init__(self, times: int = 1):
        super().__init__(times)


class PressRightArrow(Action):

    def __init__(self, times: int = 1):
        super().__init__(times)


class ScrollTo(Action):

    def __init__(self, timeout: typing.Union[int, float] = None):
        super().__init__(timeout)


class SlowScrollTo(Action):

    def __init__(self, timeout: typing.Union[int, float] = None):
        super().__init__(timeout)


class JsClick(Action):

    def __init__(self, all_matches: bool = False):
        super().__init__(all_matches)


class JsClickAll(Action):

    def __init__(self):
        super().__init__()


class JqueryClick(Action):

    def __init__(self):
        super().__init__()


class JqueryClickAll(Action):

    def __init__(self):
        super().__init__()


class HideElement(Action):

    def __init__(self):
        super().__init__()


class HideElements(Action):

    def __init__(self):
        super().__init__()


class ShowElement(Action):

    def __init__(self):
        super().__init__()


class ShowElements(Action):

    def __init__(self):
        super().__init__()


class RemoveElement(Action):

    def __init__(self):
        super().__init__()


class RemoveElements(Action):

    def __init__(self):
        super().__init__()


class ChooseFile(Action):

    def __init__(self, file_path: os.PathLike, timeout: typing.Union[int, float] = None):
        super().__init__(file_path, timeout)


class SaveElementAsImageFile(Action):

    def __init__(self,
                 file_name: os.PathLike,
                 folder: os.PathLike = None,
                 overlay_text: str = ""):
        super().__init__(file_name, folder, overlay_text)


class SetValue(Action):

    def __init__(self, text: str, timeout: typing.Union[int, float] = None):
        super().__init__(text, timeout)


class JsUpdateText(Action):

    def __init__(self, text: str, timeout: typing.Union[int, float] = None):
        super().__init__(text, timeout)


class JqueryUpdateText(Action):

    def __init__(self, text: str, timeout: typing.Union[int, float] = None):
        super().__init__(text, timeout)


class AddTourStep(Action):

    def __init__(self,
                 message: str,
                 name: str = None,
                 title: str = None,
                 theme: str = None,
                 alignment: str = None,
                 duration: typing.Union[int, float] = None):
        super().__init__(message, name, title, theme, alignment, duration)


class PostMessageAndHighlight(Action):

    def __init__(self, message):
        super().__init__(message)


class FindText(Action):

    def __init__(self, text: str, timeout: typing.Union[int, float] = None):
        super().__init__(text, timeout)


class WaitForExactTextVisible(Action):

    def __init__(self, text: str, timeout: typing.Union[int, float] = None):
        super().__init__(text, timeout)


class AssertText(Action):

    def __init__(self, text: str, timeout: typing.Union[int, float] = None):
        super().__init__(text, timeout)


class AssertExactText(Action):

    def __init__(self, text: str, timeout: typing.Union[int, float] = None):
        super().__init__(text, timeout)


class WaitForTextNotVisible(Action):

    def __init__(self, text: str, timeout: typing.Union[int, float] = None):
        super().__init__(text, timeout)


class AssertTextNotVisible(Action):

    def __init__(self, text: str, timeout: typing.Union[int, float] = None):
        super().__init__(text, timeout)

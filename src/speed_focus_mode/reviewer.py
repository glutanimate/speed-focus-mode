# -*- coding: utf-8 -*-

# Speed Focus Mode Add-on for Anki
#
# Copyright (C) 2017-2021  Aristotelis P. <https://glutanimate.com/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version, with the additions
# listed at the end of the license file that accompanied this program.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# NOTE: This program is subject to certain additional terms pursuant to
# Section 7 of the GNU Affero General Public License.  You should have
# received a copy of these additional terms immediately following the
# terms and conditions of the GNU Affero General Public License that
# accompanied this program.
#
# If not, please request a copy through one of the means of contact
# listed here: <https://glutanimate.com/contact/>.
#
# Any modifications to this file must keep this entire header intact.

"""
Modifications to the Reviewer.
"""

import os

from typing import Union, Any, TYPE_CHECKING, Tuple, Optional, List, Callable


import aqt
from aqt.qt import QKeySequence
from aqt import mw
from aqt.reviewer import Reviewer
from aqt.utils import tooltip
from aqt.sound import av_player
from aqt import gui_hooks
from aqt.reviewer import ReviewerBottomBar

from anki.hooks import wrap

if TYPE_CHECKING:
    from aqt.webview import WebContent

from .config import local_conf
from .consts import PATH_ADDON, PATH_USERFILES, MODULE_ADDON

# Support for custom alert sounds located in user_files dir

alert_name = "alert.mp3"
default_alert = os.path.join(PATH_ADDON, "sounds", alert_name)
user_alert = os.path.join(PATH_USERFILES, alert_name)

if os.path.exists(user_alert):
    ALERT_PATH = user_alert
else:
    ALERT_PATH = default_alert

PYCMD_IDENTIFIER: str = "spdf"

# TIMER HANDLING
###############################################################################


def setAnswerTimeouts(self):
    c = mw.col.decks.confForDid(self.card.odid or self.card.did)
    countdown_requested = False
    if c.get("autoAlert", 0) > 0:
        self.bottom.web.eval("spdfSetAutoAlert(%d);" % (c["autoAlert"] * 1000))

    if c.get("autoSkip") and c.get("autoAgain", 0) > 0:
        action = c.get("autoAction", "again").capitalize()
        self.bottom.web.eval(
            "spdfSetAutoAction(%d, '%s');" % (c["autoAgain"] * 1000, action)
        )
        countdown_requested = True
    elif c.get("autoAnswer", 0) > 0:
        self.bottom.web.eval("spdfSetAutoAnswer(%d);" % (c["autoAnswer"] * 1000))
        countdown_requested = True
    else:
        return

    if countdown_requested and local_conf["enableMoreTimeButton"]:
        self.bottom.web.eval("spdfShow();")
    else:
        self.bottom.web.eval("spdfHide();")


def setQuestionTimeouts(self):
    c = mw.col.decks.confForDid(self.card.odid or self.card.did)
    if not c.get("autoSkip") and c.get("autoAgain", 0) > 0:
        # keep "autoAgain" as name for legacy reasons
        action = c.get("autoAction", "again").capitalize()
        self.bottom.web.eval(
            "spdfSetAutoAction(%d, '%s');" % (c["autoAgain"] * 1000, action)
        )
        if local_conf["enableMoreTimeButton"]:
            self.bottom.web.eval("spdfShow();")
    else:
        self.bottom.web.eval("spdfHide();")


def clearAnswerTimeouts():
    reviewer = mw.reviewer
    c = mw.col.decks.confForDid(reviewer.card.odid or reviewer.card.did)
    reviewer.bottom.web.eval(
        """
        if (typeof spdfAutoAnswerTimeout !== 'undefined') {
            clearTimeout(spdfAutoAnswerTimeout);
        }
        if (typeof spdfAutoAlertTimeout !== 'undefined') {
            clearTimeout(spdfAutoAlertTimeout);
        }
    """
    )
    if c.get("autoSkip"):
        reviewer.bottom.web.eval(
            """
            if (typeof spdfAutoActionTimeout !== 'undefined') {
                clearTimeout(spdfAutoActionTimeout);
            }
        """
        )


def clearQuestionTimeouts():
    reviewer = mw.reviewer
    c = mw.col.decks.confForDid(reviewer.card.odid or reviewer.card.did)
    if not c.get("autoSkip"):
        mw.reviewer.bottom.web.eval(
            """
            if (typeof spdfAutoActionTimeout !== 'undefined') {
                clearTimeout(spdfAutoActionTimeout);
            }
        """
        )


def suspendTimers():
    if mw.state in ("review", "resetRequired"):
        mw.reviewer.bottom.web.eval(
            """
            if (typeof(spdfClearCurrentTimeout) !== "undefined") {
                spdfClearCurrentTimeout();
            };
        """
        )


def onMoreTime():
    suspendTimers()
    tooltip("Timer stopped.")


# HOOKS
###############################################################################

mw.addonManager.setWebExports(__name__, r"web.*")

reviewer_injector = f"""
<script src="/_addons/{MODULE_ADDON}/web/sfm-reviewer.js"></script>
"""

reviewer_bottom_injector = f"""
<script>
    window.spdfHotkeyMoreTime = {local_conf['hotkeyMoreTime']};
</script>
<script src="/_addons/{MODULE_ADDON}/web/sfm-bottom-bar.js"></script>
"""


def webview_message_handler(reviewer: Reviewer, message: str):
    if not mw or not mw.col or not reviewer.card:
        return

    _, action = message.split(":", 1)

    conf = mw.col.decks.confForDid(reviewer.card.odid or reviewer.card.did)

    if action == "typeans":
        if local_conf["stopWhenTypingAnswer"]:
            suspendTimers()
    elif action == "alert":
        av_player.clear_queue_and_maybe_interrupt()
        av_player.play_file(ALERT_PATH)
        timeout = conf.get("autoAlert", 0)
        tooltip(
            "Wake up! You have been looking at <br>"
            "the question for <b>{}</b> seconds!".format(timeout),
            period=1000,
        )
    elif action == "action":
        action = conf.get("autoAction", "again")

    if action == "again":
        if reviewer.state == "question":
            reviewer._showAnswer()
        reviewer._answerCard(1)
    elif action == "good":
        if reviewer.state == "question":
            reviewer._showAnswer()
        reviewer._answerCard(reviewer._defaultEase())
    elif action == "bury":
        mw.reviewer.onBuryCard()


def on_webview_did_receive_js_message(
    handled: Tuple[bool, Any],
    message: str,
    context: Union[Reviewer, ReviewerBottomBar, Any],
    *args,
):
    if isinstance(context, ReviewerBottomBar):
        reviewer = context.reviewer
    elif isinstance(context, Reviewer):
        reviewer = context
    else:
        return handled

    if not message.startswith(PYCMD_IDENTIFIER):
        return handled

    callback_value = webview_message_handler(reviewer, message)

    return (True, callback_value)


def on_webview_will_set_content(
    web_content: "WebContent", context: Union[ReviewerBottomBar, Reviewer, Any], *args
):
    if isinstance(context, Reviewer):
        web_content.body += reviewer_injector
    elif isinstance(context, ReviewerBottomBar):
        web_content.body += reviewer_bottom_injector
    else:
        return


def on_reviewer_did_show_answer(*args, **kwargs):
    setQuestionTimeouts(mw.reviewer)
    clearAnswerTimeouts()


def on_reviewer_did_show_question(*args, **kwargs):
    setAnswerTimeouts(mw.reviewer)
    clearQuestionTimeouts()


def on_state_shortcuts_will_change(state: str, shortcuts: List[Tuple[str, Callable]]):
    if state != "review":
        return
    shortcuts.append((local_conf["hotkeyMoreTime"], onMoreTime))


def on_dialog_opened(self, *args, **kwargs):
    """Suspend timers when opening dialogs"""
    suspendTimers()


def inject_web_elements():
    gui_hooks.webview_will_set_content.append(on_webview_will_set_content)
    gui_hooks.webview_did_receive_js_message.append(on_webview_did_receive_js_message)
    gui_hooks.reviewer_did_show_answer.append(on_reviewer_did_show_answer)
    gui_hooks.reviewer_did_show_question.append(on_reviewer_did_show_question)
    gui_hooks.state_shortcuts_will_change.append(on_state_shortcuts_will_change)
    # TODO: file PR
    aqt.DialogManager.open = wrap(aqt.DialogManager.open, on_dialog_opened, "after")


def initializeReviewer():
    inject_web_elements()

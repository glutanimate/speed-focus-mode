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
from typing import TYPE_CHECKING, Any, Callable, List, Tuple, Union

import aqt
from anki.hooks import wrap
from aqt import gui_hooks, mw
from aqt.reviewer import Reviewer, ReviewerBottomBar
from aqt.sound import av_player
from aqt.utils import tooltip

if TYPE_CHECKING:
    from aqt.webview import WebContent
    from anki.decks import DeckManager
    from anki.decks import DeckId, DeckConfigDict

    assert mw is not None

from .config import local_conf
from .consts import MODULE_ADDON, PATH_ADDON, PATH_USERFILES

# Support for custom alert sounds located in user_files dir

alert_name = "alert.mp3"
default_alert = os.path.join(PATH_ADDON, "sounds", alert_name)
user_alert = os.path.join(PATH_USERFILES, alert_name)

if os.path.exists(user_alert):
    ALERT_PATH = user_alert
else:
    ALERT_PATH = default_alert

PYCMD_IDENTIFIER: str = "spdf"

# ANKI API SHIMS
###############################################################################


def get_config_dict_for_deck_id(
    deck_manager: "DeckManager", deck_id: Union["DeckId", int]
) -> "DeckConfigDict":
    try:
        return deck_manager.config_dict_for_deck_id(
            did=deck_id  # type: ignore[arg-type]
        )
    except AttributeError:
        return deck_manager.confForDid(deck_id)  # type: ignore[attr-defined]


# TIMER HANDLING
###############################################################################


def set_answer_timeouts(reviewer: Reviewer):
    card = reviewer.card
    if not card:
        return

    c = get_config_dict_for_deck_id(reviewer.mw.col.decks, card.odid or card.did)
    countdown_requested = False
    if c.get("autoAlert", 0) > 0:
        reviewer.bottom.web.eval("spdfSetAutoAlert(%d);" % (c["autoAlert"] * 1000))

    if c.get("autoSkip") and c.get("autoAgain", 0) > 0:
        action = c.get("autoAction", "again").capitalize()
        reviewer.bottom.web.eval(
            "spdfSetAutoAction(%d, '%s');" % (c["autoAgain"] * 1000, action)
        )
        countdown_requested = True
    elif c.get("autoAnswer", 0) > 0:
        reviewer.bottom.web.eval("spdfSetAutoAnswer(%d);" % (c["autoAnswer"] * 1000))
        countdown_requested = True
    else:
        return

    if countdown_requested and local_conf["enableMoreTimeButton"]:
        reviewer.bottom.web.eval("spdfShow();")
    else:
        reviewer.bottom.web.eval("spdfHide();")


def set_question_timeouts(reviewer: Reviewer):
    card = reviewer.card
    if not card:
        return

    c = get_config_dict_for_deck_id(reviewer.mw.col.decks, card.odid or card.did)
    if not c.get("autoSkip") and c.get("autoAgain", 0) > 0:
        # keep "autoAgain" as name for legacy reasons
        action = c.get("autoAction", "again").capitalize()
        reviewer.bottom.web.eval(
            "spdfSetAutoAction(%d, '%s');" % (c["autoAgain"] * 1000, action)
        )
        if local_conf["enableMoreTimeButton"]:
            reviewer.bottom.web.eval("spdfShow();")
    else:
        reviewer.bottom.web.eval("spdfHide();")


def clear_answer_timeouts(reviewer: Reviewer):
    card = reviewer.card
    if not card:
        return

    c = get_config_dict_for_deck_id(reviewer.mw.col.decks, card.odid or card.did)
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


def clear_question_timeouts(reviewer: Reviewer):
    card = reviewer.card
    if not card:
        return

    c = get_config_dict_for_deck_id(reviewer.mw.col.decks, card.odid or card.did)
    if not c.get("autoSkip"):
        reviewer.bottom.web.eval(
            """
            if (typeof spdfAutoActionTimeout !== 'undefined') {
                clearTimeout(spdfAutoActionTimeout);
            }
        """
        )


def suspend_timers(reviewer: Reviewer):
    if reviewer.mw.state in ("review", "resetRequired"):
        reviewer.bottom.web.eval(
            """
            if (typeof(spdfClearCurrentTimeout) !== "undefined") {
                spdfClearCurrentTimeout();
            };
        """
        )


def on_more_time():
    suspend_timers(mw.reviewer)
    tooltip("Timer stopped.")


# HOOKS
###############################################################################

mw.addonManager.setWebExports(__name__, r"web.*")

reviewer_injector = f"""
<script src="/_addons/{MODULE_ADDON}/web/sfm-reviewer.js"></script>
"""

reviewer_bottom_injector = f"""
<script>
    window.spdfHotkeyMoreTime = "{local_conf['hotkeyMoreTime']}";
</script>
<script src="/_addons/{MODULE_ADDON}/web/sfm-bottom-bar.js"></script>
"""


def webview_message_handler(reviewer: Reviewer, message: str):
    card = reviewer.card
    if not card:
        return

    _, action = message.split(":", 1)

    deck_config = get_config_dict_for_deck_id(
        reviewer.mw.col.decks, card.odid or card.did
    )

    if action == "typeans":
        if local_conf["stopWhenTypingAnswer"]:
            suspend_timers(reviewer)
    elif action == "alert":
        av_player.clear_queue_and_maybe_interrupt()
        av_player.play_file(ALERT_PATH)
        timeout = deck_config.get("autoAlert", 0)
        tooltip(
            "Wake up! You have been looking at <br>"
            "the question for <b>{}</b> seconds!".format(timeout),
            period=1000,
        )
    elif action == "action":
        action = deck_config.get("autoAction", "again")

    if action == "again":
        if reviewer.state == "question":
            reviewer._showAnswer()
        reviewer._answerCard(1)
    elif action == "good":
        if reviewer.state == "question":
            reviewer._showAnswer()
        reviewer._answerCard(reviewer._defaultEase())
    elif action == "bury":
        reviewer.onBuryCard()


def on_webview_did_receive_js_message(
    handled: Tuple[bool, Any],
    message: str,
    context: Union[Reviewer, ReviewerBottomBar, Any],
    *args,
    **kwargs,
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
    web_content: "WebContent",
    context: Union[ReviewerBottomBar, Reviewer, Any],
    *args,
    **kwargs,
):
    if isinstance(context, Reviewer):
        web_content.body += reviewer_injector
    elif isinstance(context, ReviewerBottomBar):
        web_content.body += reviewer_bottom_injector
    else:
        return


def on_reviewer_did_show_answer(*args, **kwargs):
    reviewer = mw.reviewer
    set_question_timeouts(reviewer)
    clear_answer_timeouts(reviewer)


def on_reviewer_did_show_question(*args, **kwargs):
    reviewer = mw.reviewer
    set_answer_timeouts(reviewer)
    clear_question_timeouts(reviewer)


def on_state_shortcuts_will_change(
    state: str, shortcuts: List[Tuple[str, Callable]], *args, **kwargs
):
    if state != "review":
        return
    shortcuts.append((local_conf["hotkeyMoreTime"], on_more_time))


def on_dialog_manager_did_open_dialog(*args, **kwargs):
    """Suspend timers when opening dialogs"""
    suspend_timers(mw.reviewer)


def initialize_reviewer():
    gui_hooks.webview_will_set_content.append(on_webview_will_set_content)
    gui_hooks.webview_did_receive_js_message.append(on_webview_did_receive_js_message)
    gui_hooks.reviewer_did_show_answer.append(on_reviewer_did_show_answer)
    gui_hooks.reviewer_did_show_question.append(on_reviewer_did_show_question)
    gui_hooks.state_shortcuts_will_change.append(on_state_shortcuts_will_change)

    try:  # 2.1.47+
        gui_hooks.dialog_manager_did_open_dialog.append(  # type: ignore
            on_dialog_manager_did_open_dialog
        )
    except AttributeError:
        # Important: Need to wrap "before" as "after" overrides the patched method's
        # return value, causing other add-ons depending on open() return to fail
        aqt.DialogManager.open = wrap(
            aqt.DialogManager.open, on_dialog_manager_did_open_dialog, "before"
        )

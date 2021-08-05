/*
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
*/


var spdfAutoAlertTimeout = 0;
var spdfAutoAnswerTimeout = 0;
var spdfAutoActionTimeout = 0;
var spdfCurrentTimeout = null;
var spdfCurrentAction = null;
var spdfCurrentInterval = null;

function spdfReset() {
  clearInterval(spdfCurrentInterval);
  spdfCurrentTimeout = null;
  spdfCurrentAction = null;
}

function spdfUpdateTime() {
  var timeNode = document.getElementById("spdfTime");
  if (spdfTimeLeft === 0) {
    timeNode.textContent = "";
    return;
  }
  var time = Math.max(spdfTimeLeft, 0);
  var m = Math.floor(time / 60);
  var s = time % 60;
  if (s < 10) {
    s = "0" + s;
  }
  timeNode.textContent = spdfCurrentAction + " " + m + ":" + s;
  spdfTimeLeft = time - 1;
}

function spdfSetCurrentTimer(timeout, action, ms) {
  spdfCurrentAction = action;
  spdfCurrentTimeout = timeout;
  spdfTimeLeft = Math.round(ms / 1000);
  spdfUpdateTime();
  spdfCurrentInterval = setInterval(function () {
    spdfUpdateTime();
  }, 1000);
}

function spdfClearCurrentTimeout() {
  if (spdfCurrentTimeout != null) {
    clearTimeout(spdfCurrentTimeout);
  }
  if (spdfAutoAlertTimeout != null) {
    clearTimeout(spdfAutoAlertTimeout);
  }
  clearInterval(spdfCurrentInterval);
  var timeNode = document.getElementById("spdfTime");
  timeNode.textContent = "Stopped.";
  $("#ansbut").focus();
  $("#defease").focus();
}

function spdfSetAutoAlert(ms) {
  clearTimeout(spdfAutoAlertTimeout);
  spdfAutoAlertTimeout = setTimeout(function () {
    pycmd("spdf:alert");
  }, ms);
}

function spdfSetAutoAnswer(ms) {
  spdfReset();
  clearTimeout(spdfAutoAnswerTimeout);
  spdfAutoAnswerTimeout = setTimeout(function () {
    pycmd("ans");
  }, ms);
  spdfSetCurrentTimer(spdfAutoAnswerTimeout, "Reveal", ms);
}
function spdfSetAutoAction(ms, action) {
  spdfReset();
  clearTimeout(spdfAutoActionTimeout);
  spdfAutoActionTimeout = setTimeout(function () {
    pycmd("spdf:action");
  }, ms);
  spdfSetCurrentTimer(spdfAutoActionTimeout, action, ms);
}

function spdfHide() {
  document.getElementById("spdfControls").style.display = "none";
}
function spdfShow() {
  document.getElementById("spdfControls").style.display = "";
}

const spdfButtonHTML = `
<td id="spdfControls" width="50" align="center" valign="top" class="stat">
<span id="spdfTime" class="stattxt"></span><br>
<button title="Shortcut key: ${window.spdfHotkeyMoreTime}"
    onclick="spdfClearCurrentTimeout();">More time!</button>
</td>
`;


document.getElementById("middle").insertAdjacentHTML("afterend", spdfButtonHTML);

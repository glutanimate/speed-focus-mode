/*
# -*- coding: utf-8 -*-

# Speed Focus Mode Add-on for Anki
#
# Copyright (C) 2017-2022  Aristotelis P. <https://glutanimate.com/>
# Copyright (C) 2021  Ankitects Pty Ltd and contributors
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
*/

$deckOptions.then((options) => {
  const html = `
<div>
  <br />
  <h2>Speed Focus Mode</h2>
  <p
    >Looking for <b>Speed Focus Mode</b>'s options? You can access them them via 
    Anki's classic deck options screen. To get to the screen, simply close this
    window and go back to Anki's main screen. In the deck list, click on the gear icon
    next to a deck so that the deck menu pops up, 
    and this time hold down Shift (⇧) while clicking on "Options".
    You will find SFM's settings under the "General" tab.</p>
</div>
  `;
  options.addHtmlAddon(html, () => {});
});

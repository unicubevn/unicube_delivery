/*
 * #  Copyright (c) by The UniCube, 2023.
 * #  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
 * #  These code are maintained by The UniCube.
 */

function print_receipt(className = 'bean_page') {
    // console.log("className: ", className)
    // console.log("className: ", document.getElementsByClassName(className)[0])
    window.print(document.getElementsByClassName(className)[0])
}

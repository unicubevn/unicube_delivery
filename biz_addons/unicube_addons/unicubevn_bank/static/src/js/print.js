/*
 * #  Copyright (c) by The UniCube, 2023.
 * #  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
 * #  These code are maintained by The UniCube.
 */
HTMLElement.prototype.printMe = printMe;
function printMe(query){
  var myframe = document.createElement('IFRAME');
  myframe.domain = document.domain;
  myframe.style.position = "absolute";
  myframe.style.top = "-10000px";
  document.body.appendChild(myframe);
  myframe.contentDocument.write(this.innerHTML) ;
  setTimeout(function(){
  myframe.focus();
  myframe.contentWindow.print();
  myframe.parentNode.removeChild(myframe) ;// remove frame
  },3000); // wait for images to load inside iframe
  window.focus();
 }

function print_receipt(className ) {
			var printContents = document.getElementsByClassName(className);
            console.log(printContents)
			var originalContents = document.body.innerHTML;
			document.body.innerHTML = printContents[0].innerHTML;
			window.print();
			document.body.innerHTML = originalContents;
}


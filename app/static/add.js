const addTag = () => {
  const currentTag = document.getElementById("tagSearch").value;
  let eventTarget = document.getElementsByClassName("btn_delete");
  let bool = true;
  let idx = 1;
  for (var i = 0; i < eventTarget.length; i++) {
    if (eventTarget.item(i).innerHTML == currentTag) {
      bool = false;
    }
    if (eventTarget.item(i).name == idx) {
      idx += 1;
    }
  }
  if (currentTag.length != 0 && eventTarget.length < 3 && bool) {
    let tableID = document.getElementById("tagTable");
    let button = document.createElement("button");
    let td = document.createElement("td");
    let input = document.createElement("input");

    button.setAttribute("class", "btn_delete");
    button.setAttribute("type", "button");
    button.setAttribute("name", idx);
    button.innerHTML = currentTag;

    input.setAttribute("hidden", "hidden");
    input.setAttribute("name", idx);
    input.setAttribute("value", currentTag);

    button.appendChild(input);
    td.appendChild(button);
    tableID.appendChild(td);

    for (var i = 0; i < eventTarget.length; i++) {
      eventTarget[i].addEventListener("click", function () {
        var parent = document.querySelector("#tagTable");
        parent.removeChild(this.parentElement);
        i--;
      });
    }
  }
};

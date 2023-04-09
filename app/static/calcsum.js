function calcSum() {
  const table = document.getElementById("items");

  // 합계 계산
  let sum = 0;
  for (let i = 0; i < table.rows.length; i++) {
    sum +=
      parseInt(table.rows[i].cells[2].getElementsByTagName("input")[0].value) *
      parseInt(table.rows[i].cells[3].innerText);
  }
  document.getElementById("sum").innerText = sum;
  document.getElementById("sum1").value = sum;
}

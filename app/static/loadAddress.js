const loadAddress = () => {
  const id = document.getElementById("select_address").value;
  const address = document.getElementById(id + "_num").value;
  const base_address = document.getElementById(id + "_base").value;
  const detail_address = document.getElementById(id + "_detail").value;

  document.getElementById("address").value = address;
  document.getElementById("base_address").value = base_address;
  document.getElementById("detail_address").value = detail_address;
};

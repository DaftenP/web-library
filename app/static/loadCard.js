const loadCard = () => {
  const id = document.getElementById("select_card").value;
  const card_num = document.getElementById(id + "_num").value;
  const card_exp = document.getElementById(id + "_exp").value;
  const card_CVC = document.getElementById(id + "_CVC").value;

  document.getElementById("card_num").value = card_num;
  document.getElementById("card_exp").value = card_exp;
  document.getElementById("card_CVC").value = card_CVC;
};

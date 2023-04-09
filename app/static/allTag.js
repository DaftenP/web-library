let allTag = () => {
  const tags = document.getElementsByClassName("tags");
  let result = [];
  for (var i = 0; i < tags.length; i++) {
    result.push(tags.item(i).innerHTML);
    console.log("1");
  }
  return result;
};

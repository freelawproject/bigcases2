function showInputToSuggestCurators() {
  let suggestedCuratorsDiv = document.getElementById("suggested_curators");
  let suggestedCuratorsInput = document.getElementById("id_suggested_curators");
  suggestedCuratorsDiv.classList.remove("hidden");
  suggestedCuratorsInput.required = true;
}

function hideInputToSuggestCurators() {
  let suggestedCuratorsDiv = document.getElementById("suggested_curators");
  let suggestedCuratorsInput = document.getElementById("id_suggested_curators");
  suggestedCuratorsDiv.classList.add("hidden");
  suggestedCuratorsInput.required = false;
}

let boolean_selector = document.getElementById("id_is_curator");
boolean_selector.addEventListener("change", function () {
  if (this.value == "False") {
    showInputToSuggestCurators();
  } else {
    hideInputToSuggestCurators();
  }
});

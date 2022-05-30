// ----- Email Feedback form -----
const btn = document.getElementById('button');

emailjs.init('user_h27EblnJWkhrtRpVIjI8a');

document.getElementById('form')
  .addEventListener('submit', function (event) {
    event.preventDefault();

    btn.value = 'Thanks - we will come back to you in 24 hours';

    const serviceID = 'default_service';
    const templateID = 'template_fpmgm4c';

    emailjs.sendForm(serviceID, templateID, this)
      .then(() => {
        btn.value = 'Contact me';
        alert('Sent!');
      }, (err) => {
        btn.value = 'Contact me';
        alert(JSON.stringify(err));
      });
  });

  // ----------------- Adding an ingredient -----------------

let ingredient = 1;
let max_ingredients = 20;

$(".add_ingredient").click(function (e) {
  e.preventDefault();
  if (ingredient < max_ingredients) {
    ingredient++;
    $(".list_of_ingredients").append(`
    <div class="input-field col s12">
    <input id="recipe_ingredients${ingredient}" name="recipe_ingredients" type="text" data-length="150" 
      minlength="2" maxlength="150" class="validate" required>
    <label for="recipe_ingredients${ingredient}">Ingredient ${ingredient}.</label>
    <a type="button" class="right btn-small btn-red-ingredient remove_ingredient"><i class="fas fa-minus"></i> Remove ingredient</a></div>`);
  }
});

$("main").on('click', ".remove_ingredient", function () {
  $(this).parent('div').remove();
  ingredient--;
});

// -------------------- Dynamically adding a step ---------------------

let instruction_step = 1;
let max_instruction_steps = 20;

$(".add_instruction_step").click(function (e) {
  e.preventDefault();
  if (instruction_step < max_instruction_steps) {
    instruction_step++;
    $(".list_of_instruction_steps").append(`
    <div class="input-field col s12">
    <input id="recipe_instruction${instruction_step}" name="recipe_instruction" type="text" data-length="500" 
      minlength="5" maxlength="500" class="validate" required>
    <label for="recipe_instruction${instruction_step}">Instruction step ${instruction_step}.</label>
    <a type="button" class="right btn-small btn-red-ingredient remove_instruction_step"><i class="fas fa-minus"></i> Remove instruction step</a></div>`);
  }
});

$("main").on('click', ".remove_instruction_step", function () {
  $(this).parent('div').remove();
  instruction_step--;
});

// ---------- Ingredients and instructions lists ----------

let list = document.getElementsByClassName("collapsible-list");
let i;

for (i = 0; i < list.length; i++) {
  list[i].addEventListener("click", function() {
    this.classList.toggle("active");
    let content = this.nextElementSibling;
    if (content.style.maxHeight){
      content.style.maxHeight = null;
    } else {
      content.style.maxHeight = content.scrollHeight + "px";
    } 
  });
}
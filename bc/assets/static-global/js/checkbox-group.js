
var CheckboxGroup =  (function () {
  function CheckboxGroup(targetElement, triggerElement, removeCheckElement) {
      if (targetElement === void 0) { targetElement = null; }
      if (triggerElement === void 0) { triggerElement = null; }
      this._targetEl = targetElement;
      this._triggerEl = triggerElement;
      this._removeCheck = removeCheckElement;
      this._checked = true;
      this._init();
  }
  CheckboxGroup.prototype._init = function () {
    if (this._triggerEl) {
        this._setupEventListeners();
    }
  };
  CheckboxGroup.prototype._setupEventListeners = function () {
    var _this = this;
    this._triggerEl.addEventListener('click', function () {
      _this.check();
    });
    this._removeCheck.addEventListener('click', function () {
      _this.uncheck();
    });
  };
  CheckboxGroup.prototype.toggle = function () {
    if (this._checked) {
      this.uncheck();
    }
    else {
      this.check();
    }
  };
  CheckboxGroup.prototype.check = function () {
    this._targetEl.forEach(function ($checkbox) {
      $checkbox.checked = true;
    })
    this._checked = true;
  };
  CheckboxGroup.prototype.uncheck = function () {
    this._targetEl.forEach(function ($checkbox) {
      $checkbox.checked = false;
    })
    this._checked = false;
  };
  return CheckboxGroup;
}());


function initCheckboxes() {
  document
      .querySelectorAll('[data-cg-target]')
      .forEach(function ($triggerEl) {
      var targetClass = $triggerEl.getAttribute('data-cg-target');
      var noneButtonId = $triggerEl.getAttribute('data-cg-uncheck');
      var removeCheckButton = document.getElementById(noneButtonId)
      var $groupEl = document.querySelectorAll(`.${targetClass}`);
      if ($groupEl) {
        new CheckboxGroup($groupEl, $triggerEl, removeCheckButton);
      }
      else {
          console.error("The checkbox element with id \"".concat(targetClass, "\" does not exist. Please check the data-cg-toggle attribute."));
      }
  });
}

document.body.addEventListener("groupCheckbox", function(evt){
  initCheckboxes()
})

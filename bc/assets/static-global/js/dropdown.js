var Default = {
    triggerType: 'click',
};

var Dropdown =  (function () {
    function Dropdown(targetElement, triggerElement, closeButton,options) {
        if (targetElement === void 0) { targetElement = null; }
        if (triggerElement === void 0) { triggerElement = null; }
        if (closeButton === void 0) { closeButton = null; }
        if (options === void 0) { options = Default; }
        this._targetEl = targetElement;
        this._triggerEl = triggerElement;
        this._closeButton = closeButton;
        this._visible = false;
        this._init();
    }
    Dropdown.prototype._init = function () {
        if (this._triggerEl) {
            this._setupEventListeners();
        }
    };
    Dropdown.prototype._getTriggerEvents = function () {
        return {
            showEvents: ['click'],
            hideEvents: [],
        };
    };
    Dropdown.prototype._setupEventListeners = function () {
        var _this = this;
        var triggerEvents = this._getTriggerEvents();
        // click event handling for trigger element
        triggerEvents.showEvents.forEach(function (ev) {
            _this._triggerEl.addEventListener(ev, function () {
                _this.toggle();
            });
            if (_this._closeButton){
              _this._closeButton.addEventListener(ev, function () {
                _this.toggle();
            });
            }
        });

    };
    Dropdown.prototype._setupClickOutsideListener = function () {
        var _this = this;
        this._clickOutsideEventListener = function (ev) {
            _this._handleClickOutside(ev, _this._targetEl);
        };
        document.body.addEventListener('click', this._clickOutsideEventListener, true);
    };
    Dropdown.prototype._removeClickOutsideListener = function () {
        document.body.removeEventListener('click', this._clickOutsideEventListener, true);
    };
    Dropdown.prototype._handleClickOutside = function (ev, targetEl) {
        var clickedEl = ev.target;
        if (clickedEl !== targetEl &&
            !targetEl.contains(clickedEl) &&
            !this._triggerEl.contains(clickedEl) &&
            this.isVisible()) {
            this.hide();
        }
    };
    Dropdown.prototype.toggle = function () {
        if (this.isVisible()) {
            this.hide();
        }
        else {
            this.show();
        }
    };
    Dropdown.prototype.isVisible = function () {
        return this._visible;
    };
    Dropdown.prototype.show = function () {
        this._targetEl.classList.remove('hidden');
        this._targetEl.classList.remove('animate-fade-out');
        // Add classes to show the dropdown
        this._targetEl.classList.add('block');
        this._targetEl.classList.add("animate-fade-in");
        this._setupClickOutsideListener();
        // Update its position
        this._visible = true;
    };
    Dropdown.prototype.hide = function () {
        this._targetEl.classList.remove('animate-fade-in');
        // Add class to hide the dropdown
        this._targetEl.classList.add('animate-fade-out');
        // Disable the event listeners
        this._visible = false;
        this._removeClickOutsideListener();
    };
    return Dropdown;
}());

function initDropdowns() {
    document
        .querySelectorAll('[data-dropdown-toggle]')
        .forEach(function ($triggerEl) {
        var dropdownId = $triggerEl.getAttribute('data-dropdown-toggle');
        var closeButtonId = $triggerEl.getAttribute('data-dropdown-close-button');
        var $dropdownEl = document.getElementById(dropdownId);
        var $closeButton = document.getElementById(closeButtonId)
        if ($dropdownEl) {
            new Dropdown($dropdownEl, $triggerEl, $closeButton);
        }
        else {
            console.error("The dropdown element with id \"".concat(dropdownId, "\" does not exist. Please check the data-dropdown-toggle attribute."));
        }
    });
}

if (typeof window !== 'undefined') {
    window.Dropdown = Dropdown;
}


initDropdowns()

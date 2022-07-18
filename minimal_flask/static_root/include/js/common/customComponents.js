class SubmitButton extends HTMLElement {
    connectedCallback() {
        const textContent = this.textContent.trim();

        this.innerHTML = `
            <button
                type="submit"
                class="${this.className}"
                :class="(isSubmitting || isSubmitDisabled) ? '${this.getAttribute('submit-class')}' : ''"
                :disabled="isSubmitting || isSubmitDisabled"
            >
                <svg x-show="isSubmitting" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span x-show="!isSubmitting">${textContent}</span>
                <span x-show="isSubmitting">${this.getAttribute('submit-text') || textContent}</span>
            </button>
        `;

        this.removeAttribute('class');
    }

}

class SignInWithGoogleButton extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
            <div class="flex items-center flex-col">
                <style>
                    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@500&display=swap');
                </style>
                <div class="h-10 w-full flex justify-center">
                    <svg x-show="isSubmitting" class="animate-spin h-5 w-5 text-viola" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                </div>
                <button
                    type="submit"
                    class="flex items-center rounded-sm p-px bg-internal-google-blue hover:shadow focus:bg-internal-google-blue-dark focus:outline-none"
                    :disabled="isSubmitting || isSubmitDisabled"
                >
                    <svg width="38" height="38" viewBox="0 0 38 38" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd" clip-rule="evenodd" d="M1 0C0.447716 0 0 0.447715 0 1V37C0 37.5523 0.447715 38 1 38H37C37.5523 38 38 37.5523 38 37V1C38 0.447716 37.5523 0 37 0H1Z" fill="white"/>
                        <path fill-rule="evenodd" clip-rule="evenodd" d="M27.64 19.2045C27.64 18.5664 27.5827 17.9527 27.4764 17.3636H19V20.845H23.8436C23.635 21.97 23.0009 22.9232 22.0477 23.5614V25.8195H24.9564C26.6582 24.2527 27.64 21.9455 27.64 19.2045V19.2045Z" fill="#4285F4"/>
                        <path fill-rule="evenodd" clip-rule="evenodd" d="M19 28C21.43 28 23.4673 27.1941 24.9564 25.8195L22.0477 23.5614C21.2418 24.1014 20.2109 24.4205 19 24.4205C16.6559 24.4205 14.6718 22.8373 13.9641 20.71H10.9573V23.0418C12.4382 25.9832 15.4818 28 19 28V28Z" fill="#34A853"/>
                        <path fill-rule="evenodd" clip-rule="evenodd" d="M13.9641 20.71C13.7841 20.17 13.6818 19.5932 13.6818 19C13.6818 18.4068 13.7841 17.83 13.9641 17.29V14.9582H10.9573C10.3477 16.1732 10 17.5477 10 19C10 20.4523 10.3477 21.8268 10.9573 23.0418L13.9641 20.71V20.71Z" fill="#FBBC05"/>
                        <path fill-rule="evenodd" clip-rule="evenodd" d="M19 13.5795C20.3214 13.5795 21.5077 14.0336 22.4405 14.9255L25.0218 12.3441C23.4632 10.8918 21.4259 10 19 10C15.4818 10 12.4382 12.0168 10.9573 14.9582L13.9641 17.29C14.6718 15.1627 16.6559 13.5795 19 13.5795V13.5795Z" fill="#EA4335"/>
                    </svg>
                    <span class="mx-3 block text-white font-roboto text-sm">Sign in with Google</span>
                </button>
            </div>
        `;
    }

}

class PrettySelect extends HTMLElement {
    connectedCallback() {
        const name = this.getAttribute('name');
        const id = this.getAttribute('id');

        const isOpenOnTop = !!this.getAttribute('open-on-top');

        const options = this.getAttribute('options').replace(new RegExp('"', 'g'), '\'');
        const selected = this.getAttribute('selected');

        this.innerHTML = `
            <div
                class="relative block"
                x-data="{
                    options: ${options},
                    defaultSelected: '${selected}' || null,
                    selected: null,
                    isSelected(option) {
                        return this.selectedOption[0] == option[0];
                    },
                    placeholder: 'Select',
                    get selectedOption() {
                        if (Array.isArray(this.selected)) {
                            return this.selected;
                        }
                        if (this.defaultSelected) {
                            return this.options.find((option) => option[0] === this.defaultSelected) || [];
                        }
                        return [];
                    },
                    isOpen: false,
                    toggleOpen() {
                        this.isOpen = !this.isOpen;
                    },
                    close() {
                        this.isOpen = false;
                    },
                    onSelect(option) {
                        this.selected = option;

                        this.close();
                    },
                }">
                <input x-model="selectedOption[0]" readonly name="${name}" id="${id}" hidden/>
                <div
                    class="flex items-center justify-between cursor-pointer py-2.5 pl-3 pr-2 text-bodysmall rounded border border-gray-lighter bg-white w-80 h-10 text-gray-darkest"
                    @click="toggleOpen"
                    @keydown.escape.window="close"
                >
                    <div class="flex-1 flex items-center truncate">
                        <div
                            class="inline-block truncate select-none"
                            x-text="selectedOption[1] || placeholder"
                        ></div>
                    </div>
                    <svg
                        width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"
                        :class="isOpen ? 'ml-1 transform flex-shrink-0 rotate-180 translate-y-0.5' : 'ml-1 transform flex-shrink-0'"
                    >
                        <path d="M5 8.33325L10 13.3333L15 8.33325H5Z" fill="#BDBDC2"/>
                    </svg>
                </div>
                <ul
                    x-show="isOpen"
                    class="absolute bg-white border-0 rounded-md outline-none shadow-select-items-container z-10 max-h-60 overflow-y-auto w-80 ${isOpenOnTop ? 'bottom-11' :'top-11' } left-0"
                    @click.away="close"
                >
                    <template x-for="option in options">
                        <li
                            @click="onSelect(option)"
                            :class="isSelected(option) ? 'flex items-center justify-between select-none font-semibold cursor-pointer text-gray-900 hover:bg-gray-lighter min-h-9 px-3 py-2 text-bodysmall' : 'flex items-center justify-between select-none cursor-pointer text-gray-900 hover:bg-gray-lighter min-h-9 px-3 py-2 text-bodysmall'"
                        >
                            <span x-text="option[1]"></span>
                            <svg
                                x-show="isSelected(option)"
                                width="20" height="20" viewBox="0 0 20 20" fill="#33C89D" xmlns="http://www.w3.org/2000/svg"
                            >
                                <path d="M7.49993 13.4999L4.58327 10.5832C4.25827 10.2582 3.7416 10.2582 3.4166 10.5832C3.0916 10.9082 3.0916 11.4249 3.4166 11.7499L6.90827 15.2415C7.23327 15.5665 7.75827 15.5665 8.08327 15.2415L16.9166 6.41652C17.2416 6.09152 17.2416 5.57485 16.9166 5.24985C16.5916 4.92485 16.0749 4.92485 15.7499 5.24985L7.49993 13.4999Z" />
                            </svg>
                        </li>
                    </template>
                </ul>
            </div>
        `;
    }

}


document.addEventListener('DOMContentLoaded', function() {
    customElements.define('submit-button', SubmitButton);
    customElements.define('sign-in-with-google-button', SignInWithGoogleButton);
    customElements.define('pretty-select', PrettySelect);
})


const initSubmitButton = () => {
    return {
        'isSubmitting': false,
        'isSubmitDisabled': false,
        disableSubmitButton() {
            this.isSubmitting = true;
            this.isSubmitDisabled = true;
        }
    }
}

window.initSubmitButton = initSubmitButton;

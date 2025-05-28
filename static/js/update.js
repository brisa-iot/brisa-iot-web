// Get references to the DOM elements
const inputTypeFileRadio = document.getElementById('inputTypeFile');
const inputTypeTextRadio = document.getElementById('inputTypeText');
const fileUploadSectionDiv = document.getElementById('fileUploadSection');
const textInputSectionDiv = document.getElementById('textInputSection');
const fileInputElement = document.getElementById('file');
const jsonTextAreaElement = document.getElementById('jsonText');
const configForm = document.getElementById('configForm');

function toggleInputSections() {
    if (!inputTypeFileRadio || !inputTypeTextRadio) {
        // console.warn("Radio buttons for input type selection not found.");
        return;
    }

    if (inputTypeFileRadio.checked) {
        if(fileUploadSectionDiv) fileUploadSectionDiv.style.display = 'block';
        if(textInputSectionDiv) textInputSectionDiv.style.display = 'none';
        if(fileInputElement) fileInputElement.required = true; 
        if(jsonTextAreaElement) jsonTextAreaElement.required = false; 
    } else if (inputTypeTextRadio.checked) {
        if(fileUploadSectionDiv) fileUploadSectionDiv.style.display = 'none';
        if(textInputSectionDiv) textInputSectionDiv.style.display = 'block';
        if(fileInputElement) fileInputElement.required = false; 
        if(jsonTextAreaElement) jsonTextAreaElement.required = true; 
    }
}

if (inputTypeFileRadio) {
    inputTypeFileRadio.addEventListener('change', toggleInputSections);
}
if (inputTypeTextRadio) {
    inputTypeTextRadio.addEventListener('change', toggleInputSections);
}

document.addEventListener('DOMContentLoaded', function() {
    toggleInputSections(); 
});

if (configForm) {
    configForm.addEventListener('submit', function(event) {
        if (!inputTypeFileRadio || !inputTypeTextRadio) return;

        if (inputTypeFileRadio.checked) {
            if(jsonTextAreaElement) jsonTextAreaElement.value = ''; 
        } else if (inputTypeTextRadio.checked) {
            if(fileInputElement) fileInputElement.value = ''; 
        }
    });
}
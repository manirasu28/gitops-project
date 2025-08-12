// Custom JavaScript for TMS Admin Panel

document.addEventListener('DOMContentLoaded', function() {
    // Apply consistent styling to all form inputs
    const applyFormStyling = function() {
        // Get all input elements
        const inputs = document.querySelectorAll('input[type="text"], input[type="password"], input[type="email"], input[type="number"], input[type="url"], input[type="tel"], textarea, select');
        
        // Apply consistent styling
        inputs.forEach(input => {
            input.style.width = '100%';
            input.style.maxWidth = '500px';
            input.style.boxSizing = 'border-box';
            input.style.padding = '10px 15px';
            input.style.borderRadius = '6px';
            input.style.border = '1px solid #dee2e6';
            input.style.marginBottom = '10px';
            input.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.08)';
            
            // Add hover effect
            input.addEventListener('mouseenter', function() {
                this.style.borderColor = '#adb5bd';
            });
            
            input.addEventListener('mouseleave', function() {
                if (!this.matches(':focus')) {
                    this.style.borderColor = '#dee2e6';
                }
            });
            
            // Add focus effect
            input.addEventListener('focus', function() {
                this.style.borderColor = '#0a326e';
                this.style.boxShadow = '0 0 0 0.2rem rgba(10, 50, 110, 0.15)';
                this.style.outline = 'none';
            });
            
            input.addEventListener('blur', function() {
                this.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.08)';
            });
        });
        
        // Style form labels
        const labels = document.querySelectorAll('label');
        labels.forEach(label => {
            label.style.fontWeight = '600';
            label.style.color = '#444';
            label.style.marginBottom = '8px';
            label.style.display = 'block';
        });
        
        // Style form help text
        const helpTexts = document.querySelectorAll('.help');
        helpTexts.forEach(help => {
            help.style.color = '#6c757d';
            help.style.fontSize = '0.85rem';
            help.style.marginTop = '5px';
            help.style.fontStyle = 'italic';
        });
        
        // Style form rows
        const formRows = document.querySelectorAll('.form-row');
        formRows.forEach(row => {
            row.style.padding = '10px 0';
            row.style.marginBottom = '10px';
        });
        
        // Style datetime widget
        const datetimeWidgets = document.querySelectorAll('.datetime');
        datetimeWidgets.forEach(widget => {
            widget.style.display = 'flex';
            widget.style.flexWrap = 'wrap';
            widget.style.gap = '10px';
            widget.style.maxWidth = '500px';
            
            const datetimeInputs = widget.querySelectorAll('input');
            datetimeInputs.forEach(input => {
                input.style.flex = '1';
                input.style.minWidth = '120px';
            });
        });
        
        // Style fieldsets
        const fieldsets = document.querySelectorAll('fieldset');
        fieldsets.forEach(fieldset => {
            fieldset.style.marginTop = '20px';
            fieldset.style.marginBottom = '20px';
            fieldset.style.padding = '20px';
            fieldset.style.border = '1px solid #dee2e6';
            fieldset.style.borderRadius = '8px';
            fieldset.style.backgroundColor = '#f8f9fa';
            
            const legend = fieldset.querySelector('legend');
            if (legend) {
                legend.style.fontWeight = '600';
                legend.style.padding = '0 10px';
                legend.style.color = '#0a326e';
            }
        });
    };
    
    // Run initially
    applyFormStyling();
    
    // Reapply on any AJAX content changes (for admin dynamic forms)
    const observer = new MutationObserver(function(mutations) {
        applyFormStyling();
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
});

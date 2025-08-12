// Custom JavaScript for TMS Admin Navbar

document.addEventListener('DOMContentLoaded', function() {
    // Fix navbar layout and ensure search is in same row
    const navbar = document.getElementById('jazzy-navbar');
    if (navbar) {
        // Set explicit flexbox layout
        navbar.style.display = 'flex';
        navbar.style.flexWrap = 'nowrap';
        navbar.style.backgroundColor = '#051d42';
        navbar.style.justifyContent = 'space-between';
        navbar.style.alignItems = 'center';
        navbar.style.height = '58px';
        
        // Enhance search box
        const searchForm = navbar.querySelector('.form-inline');
        if (searchForm) {
            searchForm.style.marginLeft = 'auto';
            searchForm.style.marginRight = '2rem';
            searchForm.style.flex = '0 0 auto';
            searchForm.style.maxWidth = '400px';
            searchForm.style.minWidth = '250px';
            searchForm.style.height = '40px';
            searchForm.style.display = 'flex';
            searchForm.style.justifyContent = 'flex-end';
            
            const inputGroup = searchForm.querySelector('.input-group');
            if (inputGroup) {
                inputGroup.style.width = '100%';
                inputGroup.style.height = '40px';
                inputGroup.style.display = 'flex';
                inputGroup.style.flexDirection = 'row';
                inputGroup.style.flexWrap = 'nowrap';
                inputGroup.style.borderRadius = '50px';
                inputGroup.style.overflow = 'hidden';
                inputGroup.style.backgroundColor = 'rgba(255, 255, 255, 0.15)';
                inputGroup.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
                inputGroup.style.position = 'relative';
            }
            
            const inputGroupAppend = searchForm.querySelector('.input-group-append');
            if (inputGroupAppend) {
                inputGroupAppend.style.position = 'absolute';
                inputGroupAppend.style.right = '0';
                inputGroupAppend.style.top = '0';
                inputGroupAppend.style.height = '40px';
                inputGroupAppend.style.display = 'flex';
            }
            
            const searchInput = searchForm.querySelector('.form-control-navbar');
            if (searchInput) {
                searchInput.style.backgroundColor = 'transparent';
                searchInput.style.border = 'none';
                searchInput.style.color = 'white';
                searchInput.style.padding = '0.6rem 1.2rem';
                searchInput.style.paddingRight = '50px';
                searchInput.style.width = '100%';
                searchInput.style.height = '40px';
                
                // Add focus effects
                searchInput.addEventListener('focus', function() {
                    inputGroup.style.backgroundColor = 'rgba(255, 255, 255, 0.2)';
                    inputGroup.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
                });
                
                searchInput.addEventListener('blur', function() {
                    inputGroup.style.backgroundColor = 'rgba(255, 255, 255, 0.15)';
                    inputGroup.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
                });
            }
            
            const searchButton = searchForm.querySelector('.btn-navbar');
            if (searchButton) {
                searchButton.style.backgroundColor = 'transparent';
                searchButton.style.border = 'none';
                searchButton.style.color = 'white';
                searchButton.style.padding = '0 1.2rem';
                searchButton.style.height = '40px';
                searchButton.style.width = '50px';
                searchButton.style.position = 'relative';
                searchButton.style.zIndex = '5';
                
                // Add hover effects
                searchButton.addEventListener('mouseenter', function() {
                    this.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
                });
                
                searchButton.addEventListener('mouseleave', function() {
                    this.style.backgroundColor = 'transparent';
                });
            }
        }
        
        // Fix navbar nav menus to be in the same row
        const navbars = navbar.querySelectorAll('.navbar-nav');
        navbars.forEach(function(nav) {
            nav.style.display = 'flex';
            nav.style.flexDirection = 'row';
            nav.style.alignItems = 'center';
            nav.style.height = '100%';
            nav.style.flexWrap = 'nowrap';
        });
        
        // Fix specific issue with search button appearing in different row
        setTimeout(function() {
            // This timeout allows the DOM to fully render before making final adjustments
            const searchForm = navbar.querySelector('.form-inline');
            if (searchForm) {
                const inputGroupAppend = searchForm.querySelector('.input-group-append');
                if (inputGroupAppend) {
                    inputGroupAppend.style.position = 'absolute';
                    inputGroupAppend.style.right = '0';
                    inputGroupAppend.style.top = '0';
                    inputGroupAppend.style.height = '40px';
                    inputGroupAppend.style.display = 'flex';
                }
            }
        }, 100);
    }
});

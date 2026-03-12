/**
 * Easix Admin - Enhanced JavaScript
 * Built with Alpine.js and HTMX
 * Features: Dark Mode, Toast Notifications, Bottom Sheets, Pull-to-Refresh
 */

// ============================================
// Alpine.js Components
// ============================================

document.addEventListener('alpine:init', () => {

    // Sidebar component with collapse functionality
    Alpine.data('sidebar', () => ({
        open: false,
        collapsed: false,
        expandedGroups: {},

        toggle() {
            this.open = !this.open;
        },

        close() {
            this.open = false;
        },

        toggleCollapse() {
            this.collapsed = !this.collapsed;
            localStorage.setItem('easix-sidebar-collapsed', this.collapsed);
        },

        toggleGroup(groupId) {
            this.expandedGroups[groupId] = !this.expandedGroups[groupId];
        },

        isGroupExpanded(groupId) {
            return this.expandedGroups[groupId] || false;
        },

        isActiveUrl(pattern) {
            const currentPath = window.location.pathname;
            return currentPath.includes(pattern);
        },

        init() {
            // Restore collapsed state
            const collapsed = localStorage.getItem('easix-sidebar-collapsed');
            if (collapsed === 'true') {
                this.collapsed = true;
            }

            // Listen for sidebar toggle events
            window.addEventListener('sidebar-toggle', () => {
                this.toggle();
            });
        }
    }));

    // Dropdown component
    Alpine.data('dropdown', () => ({
        open: false,
        closeOnOutside: true,

        toggle() {
            this.open = !this.open;
        },

        close() {
            this.open = false;
        },

        init() {
            const closeOnOutside = (event) => {
                if (this.open && this.closeOnOutside && !this.$el.contains(event.target)) {
                    this.open = false;
                }
            };
            document.addEventListener('click', closeOnOutside);

            this.$watch('open', (value) => {
                if (value) {
                    this.$nextTick(() => {
                        this.$refs.menu?.focus();
                    });
                }
            });
        }
    }));

    // Modal component with accessibility
    Alpine.data('modal', () => ({
        open: false,
        loading: false,
        previousActiveElement: null,

        show() {
            this.previousActiveElement = document.activeElement;
            this.open = true;
            document.body.style.overflow = 'hidden';
            this.$nextTick(() => {
                this.$el.querySelector('[autofocus], button, input')?.focus();
            });
        },

        hide() {
            this.open = false;
            document.body.style.overflow = '';
            this.previousActiveElement?.focus();
        },

        toggle() {
            this.open ? this.hide() : this.show();
        },

        init() {
            // Close on escape
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.open) {
                    this.hide();
                }
            });
        }
    }));

    // Bottom Sheet component for mobile
    Alpine.data('bottomSheet', () => ({
        open: false,
        show() {
            this.open = true;
            document.body.style.overflow = 'hidden';
        },
        hide() {
            this.open = false;
            document.body.style.overflow = '';
        },
        toggle() {
            this.open ? this.hide() : this.show();
        }
    }));

    // Enhanced Table component
    Alpine.data('table', (config = {}) => ({
        loading: false,
        data: [],
        columns: [],
        filters: [],
        actions: [],
        bulkActions: [],

        // State
        page: 1,
        perPage: config.perPage || 25,
        total: 0,
        totalPages: 0,
        sort: config.sort || '-pk',
        search: '',
        searchDebounce: null,
        selectedRows: [],
        selectAll: false,
        visibleColumns: [],
        showFilters: false,
        filterValues: {},

        // Mobile card view
        mobileDisplay: config.mobileDisplay || [],

        // Pull to refresh
        pullToRefresh: config.pullToRefresh !== false,
        refreshing: false,
        startY: 0,
        currentY: 0,

        init() {
            // Initialize visible columns
            this.columns = config.columns || [];
            this.visibleColumns = this.columns.map(c => c.field);

            // Initialize filters
            this.filters = config.filters || [];
            this.filters.forEach(f => {
                if (f.default !== undefined) {
                    this.filterValues[f.field] = f.default;
                }
            });

            // Load initial data
            this.loadData();

            // Setup search debounce
            this.$watch('search', (value) => {
                clearTimeout(this.searchDebounce);
                this.searchDebounce = setTimeout(() => {
                    this.page = 1;
                    this.loadData();
                }, 300);
            });

            // Setup pull to refresh
            if (this.pullToRefresh) {
                this.setupPullToRefresh();
            }
        },

        setupPullToRefresh() {
            const container = this.$el;
            if (!container) return;

            container.addEventListener('touchstart', (e) => {
                if (container.scrollTop === 0) {
                    this.startY = e.touches[0].clientY;
                }
            }, { passive: true });

            container.addEventListener('touchmove', (e) => {
                if (this.startY && container.scrollTop === 0) {
                    this.currentY = e.touches[0].clientY;
                    const diff = this.currentY - this.startY;
                    if (diff > 0 && diff < 150) {
                        // Show refresh indicator
                    }
                }
            }, { passive: true });

            container.addEventListener('touchend', () => {
                if (this.startY && this.currentY) {
                    const diff = this.currentY - this.startY;
                    if (diff > 100) {
                        this.refresh();
                    }
                }
                this.startY = 0;
                this.currentY = 0;
            });
        },

        async refresh() {
            this.refreshing = true;
            await this.loadData();
            this.refreshing = false;
        },

        async loadData() {
            this.loading = true;

            try {
                const params = new URLSearchParams({
                    page: this.page,
                    per_page: this.perPage,
                    sort: this.sort,
                    search: this.search,
                });

                // Add filters
                Object.entries(this.filterValues).forEach(([key, value]) => {
                    if (value !== '' && value !== null && value !== undefined) {
                        params.append(`filter_${key}`, value);
                    }
                });

                const response = await fetch(`${config.dataUrl}?${params}`);
                const result = await response.json();

                this.data = result.rows || [];
                this.columns = result.columns || [];
                this.filters = result.filters || [];
                this.actions = result.actions || [];
                this.bulkActions = result.bulkActions || [];

                this.total = result.pagination?.total || 0;
                this.totalPages = result.pagination?.pages || 0;
                this.page = result.pagination?.page || 1;

                // Update visible columns
                this.visibleColumns = this.columns
                    .filter(c => c.visible !== false)
                    .map(c => c.field);

            } catch (error) {
                console.error('Error loading table data:', error);
                showToast('Error loading data', 'error');
            } finally {
                this.loading = false;
            }
        },

        toggleSort(field) {
            const col = this.columns.find(c => c.field === field);
            if (!col?.sortable) return;

            if (this.sort === field) {
                this.sort = `-${field}`;
            } else if (this.sort === `-${field}`) {
                this.sort = field;
            } else {
                this.sort = `-${field}`;
            }

            this.loadData();
        },

        toggleSelectAll() {
            this.selectAll = !this.selectAll;
            if (this.selectAll) {
                this.selectedRows = this.data.map(row => row.pk);
            } else {
                this.selectedRows = [];
            }
        },

        toggleSelectRow(pk) {
            const index = this.selectedRows.indexOf(pk);
            if (index === -1) {
                this.selectedRows.push(pk);
            } else {
                this.selectedRows.splice(index, 1);
            }

            this.selectAll = this.selectedRows.length === this.data.length;
        },

        isSelected(pk) {
            return this.selectedRows.includes(pk);
        },

        goToPage(page) {
            if (page < 1 || page > this.totalPages) return;
            this.page = page;
            this.loadData();
        },

        async applyBulkAction(actionName) {
            if (this.selectedRows.length === 0) {
                showToast('Please select items first', 'warning');
                return;
            }

            const action = this.bulkActions.find(a => a.action_name === actionName);
            if (action?.confirm && !confirm(action.confirm)) {
                return;
            }

            const formData = new FormData();
            formData.append('action', actionName);
            this.selectedRows.forEach(pk => formData.append('selected_ids', pk));

            try {
                const response = await fetch(config.bulkActionUrl, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: formData,
                });

                if (response.ok) {
                    this.selectedRows = [];
                    this.selectAll = false;
                    this.loadData();

                    const result = await response.json();
                    if (result.message) {
                        showToast(result.message, 'success');
                    }
                } else {
                    showToast('Action failed', 'error');
                }
            } catch (error) {
                console.error('Error applying bulk action:', error);
                showToast('Error applying action', 'error');
            }
        },

        toggleColumn(field) {
            const index = this.visibleColumns.indexOf(field);
            if (index === -1) {
                this.visibleColumns.push(field);
            } else {
                this.visibleColumns.splice(index, 1);
            }
        },

        isColumnVisible(field) {
            return this.visibleColumns.includes(field);
        },

        getSortIcon(field) {
            if (this.sort === field) return '↑';
            if (this.sort === `-${field}`) return '↓';
            return '';
        },

        getCellValue(row, field) {
            return row.cells?.[field] ?? row[field] ?? '';
        },

        formatValue(value, type) {
            if (value === null || value === undefined) return '';

            if (typeof value === 'object' && value.badge !== undefined) {
                return value;
            }

            switch (type) {
                case 'boolean':
                    return value ? 'Yes' : 'No';
                case 'date':
                    return new Date(value).toLocaleDateString();
                case 'datetime':
                    return new Date(value).toLocaleString();
                case 'number':
                    return typeof value === 'number'
                        ? value.toLocaleString()
                        : value;
                default:
                    return String(value);
            }
        },

        exportData(format = 'csv') {
            const params = new URLSearchParams({
                export: format,
                sort: this.sort,
                search: this.search,
            });
            window.location.href = `${config.dataUrl}?${params}`;
        }
    }));

    // Enhanced Form component with validation
    Alpine.data('form', (config = {}) => ({
        submitting: false,
        errors: {},
        values: config.initialValues || {},
        touched: {},

        async submit() {
            this.submitting = true;
            this.errors = {};

            // Mark all fields as touched
            Object.keys(this.values).forEach(key => {
                this.touched[key] = true;
            });

            // Validate before submit
            if (!this.validate()) {
                this.submitting = false;
                return;
            }

            try {
                const formData = new FormData(this.$el);

                const response = await fetch(this.$el.action, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: formData,
                });

                if (response.redirected) {
                    window.location.href = response.url;
                    return;
                }

                const result = await response.json();

                if (!response.ok) {
                    if (result.errors) {
                        this.errors = result.errors;
                    } else {
                        showToast(result.error || 'An error occurred', 'error');
                    }
                } else {
                    showToast('Saved successfully!', 'success');
                }
            } catch (error) {
                console.error('Form submission error:', error);
                showToast('An error occurred', 'error');
            } finally {
                this.submitting = false;
            }
        },

        validate() {
            let isValid = true;
            // Add custom validation logic here
            return isValid;
        },

        hasError(field) {
            return this.errors[field] !== undefined;
        },

        getError(field) {
            return this.errors[field];
        },

        isTouched(field) {
            return this.touched[field];
        },

        markTouched(field) {
            this.touched[field] = true;
        }
    }));

    // File upload component with drag-drop
    Alpine.data('fileUpload', (config = {}) => ({
        files: [],
        dragging: false,
        uploading: false,
        progress: 0,
        maxFiles: config.maxFiles || 10,
        acceptedTypes: config.acceptedTypes || '*',

        init() {
            const dropZone = this.$el;

            dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                this.dragging = true;
            });

            dropZone.addEventListener('dragleave', (e) => {
                e.preventDefault();
                this.dragging = false;
            });

            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                this.dragging = false;
                this.handleFiles(e.dataTransfer.files);
            });

            dropZone.addEventListener('click', () => {
                this.$refs.input?.click();
            });
        },

        handleFiles(fileList) {
            const newFiles = Array.from(fileList).slice(0, this.maxFiles - this.files.length);

            newFiles.forEach(file => {
                if (this.acceptedTypes === '*' ||
                    file.type.match(this.acceptedTypes)) {
                    this.files.push({
                        file,
                        name: file.name,
                        size: file.size,
                        type: file.type,
                        preview: file.type.startsWith('image/')
                            ? URL.createObjectURL(file)
                            : null,
                        progress: 0,
                    });
                }
            });

            this.$dispatch('files-added', { files: this.files });
        },

        removeFile(index) {
            this.files.splice(index, 1);
            this.$dispatch('files-removed', { index });
        },

        async upload(url) {
            if (this.files.length === 0) return;

            this.uploading = true;
            this.progress = 0;

            for (let i = 0; i < this.files.length; i++) {
                const fileData = this.files[i];
                const formData = new FormData();
                formData.append('file', fileData.file);

                try {
                    const xhr = new XMLHttpRequest();

                    xhr.upload.addEventListener('progress', (e) => {
                        if (e.lengthComputable) {
                            fileData.progress = (e.loaded / e.total) * 100;
                            this.progress = this.files.reduce((acc, f) => acc + f.progress, 0) / this.files.length;
                        }
                    });

                    await new Promise((resolve, reject) => {
                        xhr.addEventListener('load', () => {
                            if (xhr.status === 200) {
                                resolve(JSON.parse(xhr.responseText));
                            } else {
                                reject(new Error(xhr.responseText));
                            }
                        });
                        xhr.addEventListener('error', reject);

                        xhr.open('POST', url);
                        xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
                        xhr.send(formData);
                    });
                } catch (error) {
                    console.error('Upload error:', error);
                }
            }

            this.uploading = false;
            this.$dispatch('upload-complete', { files: this.files });
        }
    }));

    // Global Search component
    Alpine.data('globalSearch', () => ({
        open: false,
        query: '',
        results: [],
        loading: false,
        debounce: null,

        init() {
            // Keyboard shortcut
            document.addEventListener('keydown', (e) => {
                if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                    e.preventDefault();
                    this.open = !this.open;
                    if (this.open) {
                        this.$nextTick(() => {
                            this.$refs.input?.focus();
                        });
                    }
                }

                if (e.key === 'Escape' && this.open) {
                    this.open = false;
                }
            });

            // Listen for custom event
            window.addEventListener('global-search-open', () => {
                this.open = true;
            });
        },

        async search() {
            clearTimeout(this.debounce);

            if (this.query.length < 2) {
                this.results = [];
                return;
            }

            this.debounce = setTimeout(async () => {
                this.loading = true;

                try {
                    const response = await fetch(`/search/?q=${encodeURIComponent(this.query)}`);
                    const data = await response.json();
                    this.results = data.results || [];
                } catch (error) {
                    console.error('Search error:', error);
                } finally {
                    this.loading = false;
                }
            }, 300);
        },

        close() {
            this.open = false;
            this.query = '';
            this.results = [];
        }
    }));

    // Toast notifications system
    Alpine.data('toasts', () => ({
        toasts: [],
        maxToasts: 5,

        add(message, type = 'info', duration = 5000) {
            const id = Date.now();
            const toast = { id, message, type };
            
            // Limit number of toasts
            if (this.toasts.length >= this.maxToasts) {
                this.toasts.shift();
            }
            
            this.toasts.push(toast);

            if (duration > 0) {
                setTimeout(() => {
                    this.remove(id);
                }, duration);
            }
        },

        remove(id) {
            this.toasts = this.toasts.filter(t => t.id !== id);
        },

        clear() {
            this.toasts = [];
        }
    }));

    // Tabs component
    Alpine.data('tabs', (config = {}) => ({
        activeTab: config.defaultTab || 0,
        orientation: config.orientation || 'horizontal',

        select(index) {
            this.activeTab = index;
        },

        selectNext() {
            const maxIndex = this.$el.querySelectorAll('[role="tab"]').length - 1;
            this.activeTab = Math.min(this.activeTab + 1, maxIndex);
        },

        selectPrevious() {
            this.activeTab = Math.max(this.activeTab - 1, 0);
        },

        isActive(index) {
            return this.activeTab === index;
        }
    }));

    // Confirm dialog
    Alpine.data('confirm', (config = {}) => ({
        open: false,
        title: config.title || 'Are you sure?',
        message: config.message || 'This action cannot be undone.',
        confirmText: config.confirmText || 'Confirm',
        cancelText: config.cancelText || 'Cancel',
        confirmStyle: config.confirmStyle || 'danger',
        onConfirm: config.onConfirm || (() => {}),

        show(options = {}) {
            Object.assign(this, options);
            this.open = true;
        },

        hide() {
            this.open = false;
        },

        async confirm() {
            await this.onConfirm();
            this.hide();
        }
    }));

    // Notification center
    Alpine.data('notificationCenter', () => ({
        notifications: [],
        unreadCount: 0,

        get notificationCount() {
            return this.unreadCount;
        },

        init() {
            // Load notifications from localStorage or API
            const stored = localStorage.getItem('easix-notifications');
            if (stored) {
                this.notifications = JSON.parse(stored);
                this.updateUnreadCount();
            }
        },

        add(notification) {
            this.notifications.unshift({
                id: Date.now(),
                read: false,
                time: 'Just now',
                ...notification
            });
            this.updateUnreadCount();
            this.save();
            showToast(notification.title, notification.type);
        },

        markAsRead(id) {
            const notification = this.notifications.find(n => n.id === id);
            if (notification) {
                notification.read = true;
                this.updateUnreadCount();
                this.save();
            }
        },

        markAllAsRead() {
            this.notifications.forEach(n => n.read = true);
            this.unreadCount = 0;
            this.save();
        },

        updateUnreadCount() {
            this.unreadCount = this.notifications.filter(n => !n.read).length;
        },

        save() {
            localStorage.setItem('easix-notifications', JSON.stringify(this.notifications));
        }
    }));
});

// ============================================
// HTMX Extensions and Events
// ============================================

document.addEventListener('htmx:configRequest', (event) => {
    event.detail.headers['X-CSRFToken'] = getCookie('csrftoken');
});

document.addEventListener('htmx:afterRequest', (event) => {
    // Handle messages from server
    const messages = event.detail.xhr.getResponseHeader('X-Message');
    if (messages) {
        try {
            const parsed = JSON.parse(messages);
            parsed.forEach(msg => {
                showToast(msg.text, msg.level);
            });
        } catch (e) {
            // Ignore parse errors
        }
    }
});

// ============================================
// Utility Functions
// ============================================

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showToast(message, type = 'info', duration = 5000) {
    // Dispatch custom event for Alpine toast
    window.dispatchEvent(new CustomEvent('show-toast', {
        detail: { message, type, duration }
    }));

    console.log(`[TOAST ${type.toUpperCase()}] ${message}`);
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(date, format = 'short') {
    const d = new Date(date);
    if (format === 'short') {
        return d.toLocaleDateString();
    }
    if (format === 'long') {
        return d.toLocaleDateString(undefined, {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    if (format === 'relative') {
        const now = new Date();
        const diff = now - d;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);

        if (minutes < 1) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        if (days < 7) return `${days}d ago`;
        return d.toLocaleDateString();
    }
    return d.toLocaleString();
}

// ============================================
// Initialize on DOM Ready
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss alerts
    document.querySelectorAll('[data-dismissible]').forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.3s';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    // Initialize tooltips
    document.querySelectorAll('[data-tooltip]').forEach(el => {
        el.addEventListener('mouseenter', (e) => {
            const tooltip = document.createElement('div');
            tooltip.className = 'fixed z-50 px-2 py-1 text-xs text-white bg-gray-900 dark:bg-gray-700 rounded shadow-lg';
            tooltip.textContent = el.dataset.tooltip;
            tooltip.style.left = `${e.pageX + 10}px`;
            tooltip.style.top = `${e.pageY + 10}px`;
            document.body.appendChild(tooltip);
            el._tooltip = tooltip;
        });

        el.addEventListener('mouseleave', () => {
            if (el._tooltip) {
                el._tooltip.remove();
                el._tooltip = null;
            }
        });

        el.addEventListener('mousemove', (e) => {
            if (el._tooltip) {
                el._tooltip.style.left = `${e.pageX + 10}px`;
                el._tooltip.style.top = `${e.pageY + 10}px`;
            }
        });
    });

    // Handle toast events
    window.addEventListener('show-toast', (e) => {
        // This will be handled by Alpine's toasts component
        const { message, type, duration } = e.detail;
        const event = new CustomEvent('toast', { detail: { message, type, duration } });
        document.dispatchEvent(event);
    });

    // Initialize theme
    const dark = localStorage.getItem('easix-theme') === 'dark' ||
                 (!('easix-theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches);
    if (dark) {
        document.documentElement.classList.add('dark');
    }
});

// Swipe gestures for mobile navigation
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
}, { passive: true });

document.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
}, { passive: true });

function handleSwipe() {
    const swipeThreshold = 50;
    const diff = touchStartX - touchEndX;

    if (Math.abs(diff) > swipeThreshold) {
        if (diff > 0) {
            // Swipe left - could open sidebar
            console.log('Swipe left detected');
        } else {
            // Swipe right - could close sidebar or go back
            console.log('Swipe right detected');
        }
    }
}

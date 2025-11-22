// Common authentication check
function checkAuth() {
    const college_id = localStorage.getItem('college_id');
    if (!college_id) {
        window.location.href = 'admin_login.html';
        return null;
    }
    return college_id;
}
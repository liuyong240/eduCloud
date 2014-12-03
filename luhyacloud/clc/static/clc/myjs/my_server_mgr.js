function popupClosing() {
  alert('About to refresh');
  window.location.href = window.location.href;
}

function exip_edit(role, ip0) {
    url = "/clc/edit_eip/" + role + "/" + ip0;
    var left = ($(window).width() / 2) - (800 / 2);
    var top = ($(window).height() / 2) - (600 / 2);
    window.open(url, '', 'height=350,width=500,left=' + left + ',top=' + top);
}

function edit_server_permission(role, mac0) {
    url = "/clc/edit/server/permission/"+ role + "/" + mac0;
    var left = ($(window).width() / 2) - (800 / 2);
    var top = ($(window).height() / 2) - (600 / 2);
    window.open(url, '', 'height=1000,width=800,left=' + left + ',top=' + top);
}

function restart_http(url) {
    alert("I am an alert box!");
}

function restart_ssh(url) {
    alert("I am an alert box!");
}

function restart_amqp(url) {
    alert("I am an alert box!");
}

function restart_rsync(url) {
    alert("I am an alert box!");
}

function restart_dhcp(url) {
alert("I am an alert box!");
}

function restart_dns(url) {
alert("I am an alert box!");
}

function restart_ftp(url) {
alert("I am an alert box!");
}

function restart_(url) {
alert("I am an alert box!");
}
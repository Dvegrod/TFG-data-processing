
function raise_content(data, status, y) {
    console.log(status);
    // AJAX Context is THIS
    $(this).append(data);
    // Decorate windows
    $(".dialog[opened='false']").dialog({
        close: function(event, ui) {
            $(this).dialog('destroy').remove();
        },
        classes: {
            "ui-dialog": "window ui-corner-all",
            "ui-dialog-titlebar": "ui-corner-all",
        },
        width: 600,
        height: 400,
        show: {
            effect: "blind",
            duration: 500,
            easing: "swing"
        },
        minHeight: 140,
        minWidth: 200,
        resize: function() {
            $( ".accordion" ).accordion( "refresh" );
        }
    });
    // OPTIONAL PROPS
    // Agents window
    $(".dialog[opened='false'].agents:not(.select_dialog)").dialog('option', 'buttons', [{
        text: "Create new agent",
        icon: "ui-icon-plus",
        click: function() {
            launch_content('new_agent');
        }
    },{
        text: "Create new experiment",
        icon: "ui-icon-power",
        click: function() {
            launch_content('new_experiment');
        }
    }]);
    // Agent creation
    $(".dialog[opened='false'].agent_creation").dialog('option', 'buttons', [{
        text: "Create",
        icon: "ui-icon-star",
        click: function() {
            // Custom submit using ajax
            selector = $("#ag-creat");
            selector.submit(ajaxFormSubmit);
            selector.submit();
            $(this).dialog('close');
        }
    },{
        text: "Cancel",
        icon: "ui-icon-close",
        click: function() {
            $(this).dialog('close');
        }
    }]);
    // Experiment creation
    $(".dialog[opened='false'].experiment_creation").dialog('option', 'buttons', [{
        text: "Create",
        icon: "ui-icon-star",
        click: function() {
            // Custom submit using ajax
            selector = $("#ex-creat");
            selector.submit(ajaxFormSubmit);
            selector.submit();
            $(this).dialog('close');
        }
    },{
        text: "Cancel",
        icon: "ui-icon-close",
        click: function() {
            $(this).dialog('close');
        }
    }]);
    // SET TO OPENED
    $(".dialog").attr("opened", "true");
    // Decorate accordions
    $(".accordion[rendered='false']").accordion({
        collapsible : true,
        heightStyle : "content",
    });
    $(".accordion").attr("rendered", "true");
}

function raise_error(x, error, y) {
    console.log(error);
}

// Executes AJAX, adds content, launches content as a dialog
// Inputs: url (string), param (dict)
function launch_content(url, param = {}, where = "body") {
    $.ajax({
        url: url,
        data: param,
        context: $(where),
        success: raise_content,
        error: raise_error
    });
}


// Used to filter elements at front
function filter(elements_class, elements_field, constraint) {
    $(elements_class).hide();
    $(elements_class + " " + elements_field + ":contains('"+ constraint + "')").parent(elements_class).show();
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function ajaxFormSubmit(e) {
    e.preventDefault();

    var form = $(this);
    var actionUrl = form.attr('action');

    $.ajax({
        type: "POST",
        url: actionUrl,
        data: form.serialize(), // serializes the form's elements.
        success: function(data)
        {
            alert("The element was submitted successfully"); // show response from the php script.
        }
    });
}

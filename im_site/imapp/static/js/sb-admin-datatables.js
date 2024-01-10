// Call the dataTables jQuery plugin
$(document).ready(function ($) {
    $.extend($.fn.dataTable.defaults, {
        language: {
            url: "http://cdn.datatables.net/plug-ins/9dcbecd42ad/i18n/Japanese.json"
        }
    });

    $('#DesktopDataTable').dataTable({
        bProcessing: true,
    });

    $('#LaptopDataTable').dataTable({
        bProcessing: true,
    });

    $('#DisplayDataTable').dataTable({
        bProcessing: true,
    });
});

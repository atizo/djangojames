djangojames = {};
djangojames.statistics = {};
djangojames.statistics.config = null;
djangojames.statistics.chart = null;
djangojames.statistics.formatter = {};
djangojames.statistics.formatter.column = function() {
    return '' + this.x + '<br><b>' + this.series.name + '</b>: ' + this.y + ' (' + Math.round(this.percentage) + '%)';
};
djangojames.statistics.formatter.pie = function() {
    return '<b>' + this.point.name + '</b>: ' + this.y + ' %';
};

djangojames.statistics.formatter.line = function() {
    return '<span style="font-size: 9px;">' + Highcharts.dateFormat('%e. %b', this.x) + '<span><br/><b>' + this.series.name + '</b>: ' + this.y;
};

djangojames.statistics.options = {
    height : 200,
    credits : {
        enabled : false
    },
    chart : {
        renderTo : 'base-chart',
        defaultSeriesType : 'column'
    },
    title : {
        text : ''
    },
    yAxis : {
        min : 0,
        title : {
            text : ''
        }
    },
    tooltip : {
    },
    plotOptions : {
        column : {
            stacking : 'percent'
        },

        pie : {
            allowPointSelect : true,
            cursor : 'pointer',
            dataLabels : {
                enabled : true,
                color : '#000000',
                connectorColor : '#000000',
                formatter : function() {
                    return '<b>' + this.point.name + '</b>: ' + this.y + ' %';
                }
            }
        }
    },

    series : [],
    exporting : {
        enabled : false,
        url : $('input#highchart-exporting-url').val()
    }
};

djangojames.statistics.pushData = function(name, data, type, options) {
    options.series.push({
        name : name,
        data : data,
        type : type.name
    });
};

djangojames.statistics.cache = {};
djangojames.statistics.loadChart = function(config, series) {
    var options = $.extend(true, {}, djangojames.statistics.options, config.options);
    options.tooltip.formatter = djangojames.statistics.formatter[config.type.name];

    if(config.multiple_series) {
        $.each(series, function(idx, values) {
            djangojames.statistics.pushData(values[0], values[1], config.type, options);
        });
    } else {
        djangojames.statistics.pushData(config.label, series, config.type, options);
    }
    $("#main_choices").text(config.label);

    djangojames.statistics.chart = new Highcharts.Chart(options);

    $('td.singleChoices.selected').removeClass('selected');
    $('input:checked').parent().addClass('selected');
    $('#base-chart').removeClass('loader');
};

djangojames.statistics.clickChoice = function(event) {
    djangojames.statistics.chart && djangojames.statistics.chart.destroy();
    djangojames.statistics.chart = null;

    $('#base-chart').addClass('loader');

    var config_id = event.target.id.replace('id_base_', '');
    var config = djangojames.statistics.config[config_id];

    if(djangojames.statistics.cache[config_id]) {
        djangojames.statistics.loadChart(config, djangojames.statistics.cache[config_id]);
    } else {
        $.ajax({
            context : {
                'config' : config
            },
            url : config.dataurl,
            method : 'GET',
            dataType : 'json',
            success : function(series) {
                djangojames.statistics.cache[config_id] = series;
                djangojames.statistics.loadChart(config, series);
                //djangojames.loader.hide();
            }
        });
    }
};

djangojames.statistics.loadSummery = function(url) {
    $('#stats-summery').addClass('loader');
    $.getJSON(url, function(series){
        $('#stats-summery').jqoteapp('#tmpl-stats-summery', series).removeClass('loader');
    });
};

$(document).ready(function(){
	if ($('#base-stats-config').length > 0) {
	    djangojames.statistics.config = JSON.parse($('#base-stats-config').val());
	    var summery_config = JSON.parse($('#summery-config').val());
	    var choice_per_col = parseInt($("#base-choice_per_col").val(), 10);
	
	    var choiceContainer = $("#base-graph-choices");
	    var html = '<div class="float-cont"><div class="left-cnt"><table class="statistics-graph-choices"><tbody>';
	    var i = 0;
	    var main_checked = false;
	    $.each(djangojames.statistics.config, function(key, val) {
	        var checked = '';
	        if(val.selected === true) {
	            checked = ' checked="checked" ';
	        }
	        if(i % choice_per_col === 0 && i > 0) {
	            html += '</tbody></table></div>';
	            html += '<div class="left-cnt"><table class="statistics-graph-choices"><tbody>';
	        }
	        html += ('<tr><td class=""><input type="radio" name="base" ' + checked + 'id="id_base_' + key + '"></td>' + '<td class="label"><label>' + val.label + '</label></td></tr>');
	        i += 1;
	
	    });
	    html += '</tbody></table></div></div>';
	    choiceContainer.append(html);
	    choiceContainer.find('input').click(djangojames.statistics.clickChoice);
	    choiceContainer.find("input:checked").click();
	
	    if(summery_config.url) {
	        djangojames.statistics.loadSummery(summery_config.url);
	    }	
	}
});

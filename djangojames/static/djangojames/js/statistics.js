djangojames = {};
djangojames.statistics = {};
djangojames.statistics.config = {};
djangojames.statistics.chart = {};
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
    
    credits : {
        enabled : false
    },
    chart : {
        renderTo : 'base-chart',
        defaultSeriesType : 'column',
        height : 380,
        width: 620
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

    series : []
};

djangojames.statistics.pushData = function(name, data, type, options) {
    options.series.push({
        name : name,
        data : data,
        type : type.name
    });
};

djangojames.statistics.cache = {};
djangojames.statistics.loadChart = function(config, series, prefix) {
	
    var options = $.extend(true, {}, djangojames.statistics.options, config.options);
    options.chart.renderTo = options.chart.renderTo + prefix;
    options.tooltip.formatter = djangojames.statistics.formatter[config.type.name];

    if(config.multiple_series) {
        $.each(series, function(idx, values) {
            djangojames.statistics.pushData(values[0], values[1], config.type, options);
        });
    } else {
        djangojames.statistics.pushData(config.label, series, config.type, options);
    }
    $("#main_choices"+prefix).text(config.label);
    djangojames.statistics.chart[prefix] = new Highcharts.Chart(options);
    $('td.singleChoices.selected').removeClass('selected');
    $('input:checked').parent().addClass('selected');
    $('#base-chart'+prefix).removeClass('loader');
};

djangojames.statistics.extract_prefix = function(target_id) {
	return '_' + target_id.split('_')[1];
};

djangojames.statistics.clickChoice = function(event) {

    var config_id = event.target.id.replace('id_base_', '');
    var prefix = djangojames.statistics.extract_prefix(config_id);	
	
    djangojames.statistics.chart[prefix] && djangojames.statistics.chart[prefix].destroy();
    djangojames.statistics.chart[prefix] = null;

    $('#base-chart'+prefix).addClass('loader');
    var config = djangojames.statistics.config[prefix][config_id];

    if(djangojames.statistics.cache[config_id]) {
        djangojames.statistics.loadChart(config, djangojames.statistics.cache[config_id], prefix);
    } else {
        $.ajax({
            context : {
                'config' : config
            },
            url : config.dataurl,
            method : 'GET',
            dataType : 'json',
            success : function(series) {
            	
            	if (series.length > 0) {
            		djangojames.statistics.cache[config_id] = series;
            	}
                djangojames.statistics.loadChart(config, series, prefix);
            }
        });
    }
};

$(document).ready(function(){
	$.each($('.stats-prefix'), function(index, value) { 
		var prefix = '_' + $(value).val();

	    djangojames.statistics.config[prefix] = JSON.parse($('#base-stats-config'+prefix).val());
	    var choice_per_col = parseInt($("#base-choice_per_col"+prefix).val(), 10);
	
	    var choiceContainer = $("#base-graph-choices"+prefix);
	    var html = '<div class="float-cont"><div class="left-cnt"><table class="statistics-graph-choices"><tbody>';
	    var i = 0;
	    var main_checked = false;
	    $.each(djangojames.statistics.config[prefix], function(key, val) {
	        var checked = '';
	        if(val.selected === true) {
	            checked = ' checked="checked" ';
	        }
	        if(i % choice_per_col === 0 && i > 0) {
	            html += '</tbody></table></div>';
	            html += '<div class="left-cnt"><table class="statistics-graph-choices"><tbody>';
	        }
	        html += ('<tr><td class=""><input type="radio" name="' + prefix + '" ' + checked + 'id="id_base_' + key + '"></td>' + '<td class="label"><label>' + val.label + '</label></td></tr>');
	        i += 1;
	
	    });
	    html += '</tbody></table></div></div>';
	    choiceContainer.append(html);
	    choiceContainer.find('input[name='+prefix+']').click(djangojames.statistics.clickChoice);
	    choiceContainer.find('input[name='+prefix+']:checked').click();
	});
});

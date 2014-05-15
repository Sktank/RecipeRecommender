/**
 * Created with PyCharm.
 * User: spencertank
 * Date: 5/6/14
 * Time: 9:35 PM
 * To change this template use File | Settings | File Templates.
 */


$(function () {

    var names;
    var topFactors;
    var recipeFactors;
    var itopFactors;
    var recipeIFactors;

    // constructs the suggestion engine
    var recipes = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        // `states` is an array of state names defined in "The Basics"
        limit: 15,
        prefetch: {
            ttl: 1,
            // url points to a json file that contains an array of country names, see
            // https://github.com/twitter/typeahead.js/blob/gh-pages/data/countries.json
            url: '../recipe-names',
            // the json file contains an array of strings, but the Bloodhound
            // suggestion engine expects JavaScript objects so this converts all of
            // those strings
            filter: function(list) {
                console.log("filtering");
                console.log(list);
//                var data = $.parseJSON(list);
                names = list.names.names;
                topFactors = list.topFactors;
                recipeFactors = list.recipeFactors;
                itopFactors = list.itopFactors;
                recipeIFactors = list.recipeIFactors;

                $("#recipe-input").prop("disabled", false);
                $("#recipe-input").prop("placeholder", "Enter Recipe");

                return $.map(list.names.names, function(recipe) { return { name: recipe }; });
            }
        }
    });

    // kicks off the loading/processing of `local` and `prefetch`
    recipes.initialize();

    $('#recipe-input').typeahead(
        null,
        {
            name: 'recipes',
            displayKey: 'name',
            // `ttAdapter` wraps the suggestion engine in an adapter that
            // is compatible with the typeahead jQuery plugin
            source: recipes.ttAdapter()
        });

    console.log("loaded");

    var y = 0;
    var x = 0;
    var numRecipes = 0;
    var myRecipes = [];

    function scrollBottom(elemId) {
        var element    = $('#' + elemId);
        var h = element[0].scrollHeight;
        element.scrollTop(h);
    }

    var romanNumerals = {
        0: "I",
        1: "II",
        2: "III",
        3: "IV",
        4: "V"
    };

    $('#recipe-input').keypress(function(e) {
        console.log(names);
        console.log(e);
        var code = e.keyCode || e.which;
        if(code == 13) {
            var input = $('#recipe-input').val();
            console.log(input);
            console.log(names.indexOf(input));
            if (names.indexOf(input) >= 0) {
                numRecipes += 1;
                x = (numRecipes.toString().length) * 13;
                $('#recipe-input').typeahead('val', '');
                $('#recipe-input').val('');
                $('#input-container').append("<div id='ipt' class='input-item'>" + input + "</div>");
                var height = $("#ipt").css("height");
                var heightVal = parseInt(height.substring(0, height.length - 2));
                $('#box-container').css('margin-top', '-=' + height);
                $("#ipt").animate({
                    top: "+=" + (y + ($('#recipe-box').offset().top - $('#recipe-input').offset().top) + 17) + "px",
                    left: "+=" + (24 + x) + "px",
                    color: "white"
                }, 600, function() {
                    console.log("done");
                    $('#box-container').css('margin-top', '+=' + height);

                    $('#recipe-box').append("<div class='recipe' id='recipe" + numRecipes + "'>" + numRecipes + ". " + $("#ipt").text() + "</div>");
                    $('#recipe-box').append("<div class='irecipe' style='margin-top:-" + height + "' id='irecipe" + numRecipes + "'>" + numRecipes + ". " + $("#ipt").text() + "</div>");

                    myRecipes.push($("#ipt").text());
                    scrollBottom('recipe-box');

                    var factors = recipeFactors[input];
                    var factorsHTML = "";
                    for (var i = 0; i < factors.length; i++) {
                        factorsHTML = factorsHTML + "<strong>" + parseFloat(Math.round(factors[i][1] * 100)) + "%</strong><br>";
                        console.log(topFactors[factors[i][0]]);
                        for (var j = 0; j < topFactors[factors[i][0]].length; j++) {
                            factorsHTML = factorsHTML + topFactors[factors[i][0]][j];
                            if (j != topFactors[factors[i][0]].length - 1) {
                                factorsHTML = factorsHTML + " <strong>&middot;</strong> ";
                            }
                        }
                        if (i != factors.length - 1) {
                            factorsHTML = factorsHTML + "<br><br>";
                        }
                    }

                    $("#recipe" + numRecipes).tooltip({
                        html: true,
                        title: "<div class='recipe-factors-title'>Recipe Factors</div><br><div>" + factorsHTML + "</div>",
                        placement: "left"
                    });

                    var ifactors = recipeIFactors[input];
                    var ifactorsHTML = "";
                    var length = Math.min(ifactors.length, 5);
                    for (i = 0; i < length; i++) {
                        ifactorsHTML = ifactorsHTML + "<strong>" + parseFloat(Math.round(ifactors[i][1] * 100)) + "%</strong><br>";
                        console.log(itopFactors[ifactors[i][0]]);
                        for (j = 0; j < itopFactors[ifactors[i][0]].length; j++) {
                            ifactorsHTML = ifactorsHTML + itopFactors[ifactors[i][0]][j];
                            if (j != itopFactors[ifactors[i][0]].length - 1) {
                                ifactorsHTML = ifactorsHTML + " <strong>&middot;</strong> ";
                            }
                        }
                        if (i != ifactors.length - 1) {
                            ifactorsHTML = ifactorsHTML + "<br><br>";
                        }
                    }

                    $("#irecipe" + numRecipes).tooltip({
                        html: true,
                        title: "<div class='recipe-factors-title'>Ingredient Factors</div><br><div>" + ifactorsHTML + "</div>",
                        placement: "right"
                    });

                    function initIngredientTooltip(num) {
                        $("#recipe" + num).mouseenter(function() {
                            console.log("in");
                            $("#irecipe" + num).tooltip('show')
                        });
                        $("#recipe" + num).mouseleave(function() {
                            console.log("out");
                            $("#irecipe" + num).tooltip('hide')
                        });
                    }

                    initIngredientTooltip(numRecipes);


                    $("#ipt").remove();
                    if (y < 350) {
                        y += heightVal;
                        console.log(y);
                        if (y > 350) {
                            y = 350;
                        }
                    }
                });
            }
        }
    });

    var opts = {
        lines: 15, // The number of lines to draw
        length: 15, // The length of each line
        width: 17, // The line thickness
        radius: 8, // The radius of the inner circle
        corners: 1, // Corner roundness (0..1)
        rotate: 28, // The rotation offset
        direction: 1, // 1: clockwise, -1: counterclockwise
        color: '#573B2E', // #rgb or #rrggbb
        speed: 1, // Rounds per second
        trail: 52, // Afterglow percentage
        shadow: true, // Whether to render a shadow
        hwaccel: false, // Whether to use hardware acceleration
        className: 'spinner', // The CSS class to assign to the spinner
        zIndex: 2e9, // The z-index (defaults to 2000000000)
        top: '113px', // Top position relative to parent in px
        left: '50%' // Left position relative to parent in px
    };

    function getRecs(button, alg, box) {
        var self = button;
        if ($(self).prop("disabled"))
            return false;
        if (myRecipes.length > 0) {
            $(self).prop("disabled", true);
            $(self).css("cursor", "not-allowed");
            $('#' + box).empty()
            var target = document.getElementById(box);
            var spinner = new Spinner(opts).spin(target);
            console.log("clicked");
            $.ajax({
                crossDomain: false,
                type: "POST",
                data: {
                    recipes: myRecipes,
                    alg: alg
                },
                url: "/recommendRecipes"
            }).success(function(data) {
                    console.log(data);
                    $('#' + box).empty().html(data);
                    $(self).removeProp("disabled");
                    $(self).css("cursor", "pointer");
                });
        }
        else {
            $('#' + box).empty().html("<h4>Your Recipe Board is Empty!</h4>");
        }
    }

    $("#btn-recommend1").click(function() {
        getRecs(this, "content", "recs1");
    });

    $("#btn-recommend2").click(function() {
        getRecs(this, "cf", "recs2");
    });

    $("#btn-recommend3").click(function() {
        getRecs(this, "hybrid", "recs3");
    });

    $("#btn-trash").click(function () {
        numRecipes = 0;
        myRecipes.length = 0;
        y = 0;
        x = 0;
        $("#recipe-box").children().fadeOut(500, function() { $("#recipe-box").empty() });
        $('#recs1').empty();
        $('#recs2').empty();
        $('#recs3').empty();
    });



});
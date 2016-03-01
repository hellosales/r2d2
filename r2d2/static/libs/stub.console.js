(function(){
    //stub out firebug console object
    //      will allow console statements to be left in place
    if (typeof Function.empty != 'function') Function.empty = function(){};

    if (typeof console == 'undefined') console = {};

    if (typeof console.log == 'undefined') console.log = Function.empty;

    if (typeof console.debug == 'undefined') console.debug = log;

    if (typeof console.info == 'undefined') console.info = log;

    if (typeof console.warn == 'undefined') console.warn = log;

    if (typeof console.error == 'undefined') console.error = log;

    if (typeof console.assert == 'undefined') console.assert = function(){
        var args = Array.prototype.slice.call(arguments);
        var parm = args.shift();
        if (!parm) {
            console.error(arguments);
            throw new Error("Assert failed.");
        }
    };

    if (typeof console.dir == 'undefined') console.dir = function(input) { 
        if (typeof JSON != 'undefined' && typeof JSON.stringify == "function")
            console.log( JSON.stringify(input) );
        else
            console.log(input.toString());
    };

    if (typeof console.dirxml == 'undefined') console.dirxml = console.dir;

    if (typeof console.trace == 'undefined') console.trace = Function.empty;
    if (typeof console.group == 'undefined') console.group = Function.empty;
    if (typeof console.groupCollapsed == 'undefined') console.groupCollapsed = Function.empty;
    if (typeof console.groupEnd == 'undefined') console.groupEnd = Function.empty;
    if (typeof console.time == 'undefined') console.time = Function.empty;
    if (typeof console.timeEnd == 'undefined') console.timeEnd = Function.empty;
    if (typeof console.profile == 'undefined') console.profile = Function.empty;
    if (typeof console.profileEnd == 'undefined') console.profileEnd = Function.empty;
    if (typeof console.count == 'undefined') console.count = Function.empty;

    function log() {
        if (typeof JSON != "undefined" && typeof JSON.stringify == "function") return console.log(JSON.stringify(arguments));
        return console.log(arguments.toString());
    }
}());
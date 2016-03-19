var sys = {
    print: function(arg) {
        if(arg.constructor == Array) {
            return '[' + [].join.apply(arg, [', ']) + ']';
        }
        return arg;
    },
    log: function() {
        console.log([].join.apply(
            [].map.apply(arguments, [sys.print]), [' '])); }
};
exports = sys;

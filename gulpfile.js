var gulp = require('gulp');
var compass = require('gulp-compass');
var path = require('path');

var paths = {
  styles: {
    src:  '{{ project_name }}/static/scss/*',
    dest: '{{ project_name }}/static/.sass-cache'
  }
};

gulp.task('compass', function () {
  return gulp.src(paths.styles.src+'scss')
    .pipe(compass({
        sourcemap: true,
        project: path.join(__dirname, '{{ project_name }}/static'),
        css: '.sass-cache',
        sass: 'scss',
    }))
    .pipe(gulp.dest(paths.styles.dest));
});

gulp.task('watch', function() {
    gulp.watch(paths.styles.src+'*/*.scss', ['compass']);
});

gulp.task('default', ['compass','watch']);

module.exports = function (grunt) {
    /*
        Grunt installation:
        -------------------
            npm install -g grunt-cli

        Project Dependencies:
        ---------------------
            npm install
    */

    // Project configuration.
    grunt.initConfig({
        staticPath: 'stats/static',

        // Store your Package file so you can reference its specific data whenever necessary
        pkg: grunt.file.readJSON('package.json'),

        requirejs: {
            options: {
                baseUrl: '<%=staticPath%>/js/js-modules/',
                dir: '<%=staticPath%>/js/modules',
                // Only optimize modules that we have explicitly defined in
                // the modules array, don't minify any other single modules
                skipDirOptimize: true,
                // Don't try and optimize any css files found
                optimizeCss: false,
                modules: [
                    { name: 'userinfo' },
                    { name: 'main' }
                ],
                paths: {

                },

                generateSourceMaps: true,
                preserveLicenseComments: false
            },
            dev: {
                options: {
                    optimize: 'uglify2'
                }
            },
            dist: {
                options: {
                    optimize: 'uglify'
                }
            }
        },

        compass: {
            options: {
                bundleExec: true,
                config: '<%=staticPath%>/conf/compass.rb'
            },
            dev: {
                options: {
                    environment: 'development'
                }
            },
            dist: {
                options: {
                    environment: 'production',
                    force: true
                }
            }
        },

        // Run: `grunt watch` from command line for this section to take effect
        watch: {
            options: {
              nospawn: true,
              livereload: true
            },
            scripts: {
                files: [
                    '<%=staticPath%>/js/js-modules/**/*.js'
                ],
                tasks: ['requirejs:dev']
            }
        }

    });

    // Load NPM Tasks
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-requirejs');
    grunt.loadNpmTasks('grunt-contrib-compass');


    // Default Task
    grunt.registerTask('default', ['requirejs:dev']);
};

// Plugins needed to execute this:
//  Pipeline
//  NodeJS
//  checkstyle
node('python27') {
    stage('Build') {
        checkout([$class: 'SubversionSCM', locations: [[local: '.', remote: 'https://zmslabs.org/svn/zmslabs/ZMS/trunk']], workspaceUpdater: [$class: 'UpdateWithCleanUpdater']])
/*        env.NODEJS_HOME = "${tool 'default-npm'}"*/
/*        env.PATH="${env.NODEJS_HOME}/bin:${env.PATH}"*/
/*        sh 'npm install'*/
        
        sh "virtualenv ./virtualenv"
        sh "./virtualenv/bin/pip install --upgrade setuptools"
        sh "./virtualenv/bin/pip install --upgrade pip wheel"
        sh "./virtualenv/bin/pip install --requirement requirements.txt"
        sh "./virtualenv/bin/pip install --requirement selenium_tests/requirements.txt"
        sh "./virtualenv/bin/pip install --requirement unit_tests/requirements.txt"
        sh "./virtualenv/bin/pip install --editable ."
/* not required yet */
/*        sh "./virtualenv/bin/python setup.py sdist"*/
/*        archiveArtifacts artifacts: 'dist/ZMS3-*.tar.gz', fingerprint: true*/
    }
/*    stage('jshint') {
        sh '$(npm bin)/jshint --extract=never --reporter=checkstyle . > data/testing/output/jshint_checkstyle.xml || true'
        checkstyle pattern: 'data/testing/output/jshint_checkstyle.xml'
    }
*/
    stage('Unit Tests') {
        try {
            withEnv(['PATH+ZMS=./virtualenv/bin']) {
                sh "./virtualenv/bin/nosetests --processes 10 --with-xunit unit_tests || true"
            }
        } finally {
           junit 'nosetests.xml'
        }
    }
    stage('AC Tests') {
        try {
            wrap([$class: 'Xvfb',
                    displayNameOffset: 200, installationName: 'main',
                    screen: '1280x1024x16']) {
                sh "~/bin/run_ac_test"
            }
        } finally {
            junit '**/junit.xml'
        }
    }
    
    post {
        always {
            script {
                if (currentBuild.currentResult == "ABORTED" || currentBuild.currentResult == "FAILURE") {
                    // Send an email only if the build status has changed from green/unstable to red
                    emailext subject: '$DEFAULT_SUBJECT',
                        body: '$DEFAULT_CONTENT',
                        recipientProviders: [
                            [$class: 'CulpritsRecipientProvider'],
                            [$class: 'DevelopersRecipientProvider'],
                            [$class: 'RequesterRecipientProvider']
                        ], 
                        replyTo: '$DEFAULT_REPLYTO',
                        to: '$DEFAULT_RECIPIENTS'
                    }
                }
            }
        }
    }
}


pipeline {
    agent {label 'sama5d2-test-node'}
    stages {
        stage('Check out artifact') {
            steps {
                sh '''
                cleanWs()
                cd flash_test/SAMA5D2_flash
                rm -rf *.wic*
                wget http://sevikci01.creatorctek.local:8080/job/oe-build/job/master/lastSuccessfulBuild/artifact/deploy-sama5d27-wlsom1-ek/gm-ccu-dev-image-sama5d27-wlsom1-ek-sd.wic
                '''
            }
        }
        stage('deploy') {
            steps {
                sh '''
                cd flash_test/SAMA5D2_flash
                bash sama5d2_flash sama5d27-wlsom1-ek gm-ccu-dev-image-sama5d27-wlsom1-ek-sd.wic
                '''
            }
        }
        stage('Run') {
            steps {
                echo 'RUN'
            }
        }
    }
    post {
        success { gerritReview score:1 }
        unstable { gerritReview score:0 }
        failure { gerritReview score:-1 }
        always {
            cleanWs(cleanWhenNotBuilt: false,
                    deleteDirs: true,
                    disableDeferredWipeout: true,
                    notFailBuild: true,
                    patterns: [[pattern: '.gitignore', type: 'INCLUDE'],
                               [pattern: '.propsfile', type: 'EXCLUDE']])
        }
    }
}


pipeline {
    agent {label 'sama5d2'}
    stages {
        stage('Check out artifact') {
            steps {
                sh '''
                cd SAMA5D2_flash
                rm -rf '*sama5d2*'
                wget http://sevikci01.creatorctek.local:8080/job/oe-build/job/master/lastSuccessfulBuild/artifact/deploy-sama5d27-wlsom1-ek/gm-ccu-dev-image-sama5d27-wlsom1-ek-sd.wic
                '''
            }
        }
        stage('deploy') {
            steps {
                sh '''
                cd SAMA5D2_flash
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
        success { echo ' ' }
        unstable { echo 'HMMMMM' }
        failure { echo 'NOOOOOO' }
    }
}

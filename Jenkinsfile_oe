pipeline {
    agent {label 'sama5d2'}
    stages {
        stage('Check out artifact') {
            steps {
                sh "wget http://sevikci01.creatorctek.local:8080/job/GUI_Manager/job/main/lastSuccessfulBuild/artifact/build-gm-ccu/guimanager"                
            }
        }
        
        stage('deploy') {
            steps {
                sh '''
                sshpass -p "root" ssh root@192.168.7.2 \'
                cd /mnt/data/etc
                rm -rf test
                ls
                exit
                \'
                sshpass -p "root"  scp guimanager root@192.168.7.2:/mnt/data/etc
                rm guimanager

                '''
            }
        }
        
        stage('Run') {
            steps {
                echo 'Running'
                sh '''sshpass -p "root" ssh root@192.168.7.2 \'
                cd /mnt/data/etc
                if [ -f "guimanager" ]
                then
                    guimanager
                fi
                exit
                \'  
                
                ''' 
            }
        }
        
    }
    post {
        success { echo ' '}
        unstable { echo 'HMMMMM' }
        failure { echo 'NOOOOOO' }
    }
}

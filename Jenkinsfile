pipeline {
    agent any

    options { skipDefaultCheckout() }

    environment {
        AWS_DEFAULT_REGION = 'us-east-1'
    }

    stages {
        stage('Get code') {
            steps {
                echo 'Obtenemos el código fuente'
                checkout scm

                stash name:'codigo', includes:'**'
                sh 'ls -la'

                deleteDir() 

                echo 'Descargando configuración en la raíz...'
                git branch: 'production', url: 'https://github.com/viiilaaa/todo-list-aws-config.git'
                
                sh 'ls -la'

                stash name: 'config-aws', includes: 'samconfig.toml'
            }
        }

        stage('Deploy') {
            steps {
                unstash name:'codigo'
                unstash name:'config-aws'

                echo 'Desplegamos la aplicación en el entorno de PRODUCCIÓN'
                
                sh 'sam build --template todo_list-aws/template.yaml'
                sh 'sam validate --template todo_list-aws/template.yaml'
                
                
                sh """
                    sam deploy \
                    --template-file .aws-sam/build/template.yaml \
                    --config-file ${WORKSPACE}/samconfig.toml \
                    --resolve-s3 \
                    --no-confirm-changeset \
                    --no-fail-on-empty-changeset
                """
            }
            post { always { cleanWs() } }   
        }

        stage('Rest test') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    
                    unstash name:'codigo'

                    sh '''
                        BASE_URL=$(aws cloudformation describe-stacks --stack-name todo-list-aws-production --query 'Stacks[0].Outputs[?OutputKey==`BaseUrlApi`].OutputValue' --region us-east-1 --output text)
                        echo "BASE_URL Production: $BASE_URL"
                        export BASE_URL                        

                        pytest --junitxml=result-rest.xml todo_list-aws/test/integration/todoApiROTest.py
                        '''
                    junit 'result-rest.xml'
                }
            }
            post { always { cleanWs() } }   
        }
    }
}
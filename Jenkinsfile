pipeline {
    agent any

    options { skipDefaultCheckout() }

    environment {
        AWS_DEFAULT_REGION = 'us-east-1'
    }

    stages {
        stage('Get code') {
            steps {
                echo 'Obteniendo el código fuente de la rama master'
                
                checkout scm
                stash name:'codigo', includes:'**'
                sh 'ls -la'
            }
        }

        stage('Deploy') {
            steps {
                unstash name:'codigo'

                echo 'Desplegamos la aplicación en el entorno de PRODUCCIÓN'
                
                sh 'sam build --template todo_list-aws/template.yaml'
                sh 'sam validate --template todo_list-aws/template.yaml'
                
                
                sh """
                    sam deploy \
                    --template-file .aws-sam/build/template.yaml \
                    --config-file ${WORKSPACE}/todo_list-aws/samconfig.toml \
                    --config-env production \
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

                        pytest -k "get" --junitxml=result-rest.xml todo_list-aws/test/integration/todoApiTest.py
                        '''
                    junit 'result-rest.xml'
                }
            }
            post { always { cleanWs() } }   
        }
    }
}
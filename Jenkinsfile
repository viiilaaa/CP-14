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

                sh 'echo "NOMBRE RAMA: ${BRANCH_NAME}"'
                sh 'echo "GIT BRANCH: ${GIT_BRANCH}"'

                stash name:'codigo', includes:'**'
                sh 'ls -la'
            }
        }
        stage('Static test') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    unstash name:'codigo'
                    sh '''
                        python3 -m flake8 --exit-zero --format=pylint todo_list-aws/src>flake8.out
                        '''
                    sh '''
                        python3 -m bandit -r todo_list-aws -f custom -o bandit.out --msg-template "{abspath}:{line}: [{test_id}] {severity}: {msg}" || true
                        '''
                    recordIssues qualityGates: [[threshold: 8, type: 'TOTAL', unstable: true], [threshold: 10, type: 'TOTAL', unstable: false]], tools: [flake8(name: 'Flake8',pattern: 'flake8.out'),pyLint(name: 'Bandit',pattern: 'bandit.out')]
                }
            }
            post { always { cleanWs() } }   
        }
        stage('Deploy') {
            steps {
                unstash name:'codigo'

                echo 'Desplegamos la aplicación'
                sh 'sam build --template todo_list-aws/template.yaml'
                sh 'sam validate --template todo_list-aws/template.yaml'
                
                sh 'ls -la'
                sh 'ls -la ./todo_list-aws'

                sh """
                    sam deploy \
                    --template-file .aws-sam/build/template.yaml \
                    --config-file ${WORKSPACE}/todo_list-aws/samconfig.toml \
                    --config-env staging \
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
                        BASE_URL=$(aws cloudformation describe-stacks --stack-name todo-list-aws-staging --query 'Stacks[0].Outputs[?OutputKey==`BaseUrlApi`].OutputValue' --region us-east-1 --output text)
                        echo "BASE_URL: $BASE_URL"
                        export BASE_URL                        

                        pytest --junitxml=result-rest.xml todo_list-aws/test/integration/todoApiTest.py
                        '''
                    junit 'result-rest.xml'
                }
            }
            post { always { cleanWs() } }   
            
        }
        stage('Promote') {
            steps {

                checkout scm

                sh 'ls -la'
                
                script {
                    withCredentials([
                        usernamePassword(
                            credentialsId: 'github-token',
                            usernameVariable: 'GIT_USER',
                            passwordVariable: 'GIT_TOKEN'
                        )
                    ]) {
                        sh '''

                            git fetch origin

                            git checkout -B master origin/master

                            git merge --no-commit origin/develop || true

                            git checkout HEAD -- Jenkinsfile
                            git add Jenkinsfile

                            git commit -m "Auto-merge develop to master" || echo "Nada que commitear"

                            git push https://$GIT_USER:$GIT_TOKEN@github.com/viiilaaa/CP-14.git master
                        '''
                    }
                }
                
            }
        }
        post { always { cleanWs() } } 
    }
}
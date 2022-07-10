# Heading A2

## Sub-Heading A2 1

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc fringilla volutpat odio, nec iaculis tortor laoreet vitae. Suspendisse dictum nibh nulla, non fringilla sapien mollis sed. Nunc vehicula facilisis tellus, ut tempor massa bibendum sed. Aenean non justo eu nulla luctus aliquam. Nullam eget arcu a urna ultrices volutpat lobortis ut sapien. Fusce vitae dapibus tellus, nec tincidunt metus. Etiam scelerisque orci ac ligula fermentum rhoncus. Ut at nisi quis tellus imperdiet porta. In semper mollis urna, nec ultricies purus bibendum non.

## Sub-Heading A2 2

Etiam et sollicitudin dui, at tempor nulla. Suspendisse vitae scelerisque metus. Curabitur efficitur elementum felis id molestie. Proin auctor nulla nec tellus rhoncus, a rhoncus quam volutpat. Integer faucibus nisl et augue tincidunt convallis. Sed aliquet justo vel risus tempus, fringilla ultrices tortor fringilla. Nullam enim metus, commodo eu mi consequat, tincidunt varius nisi. Vestibulum aliquam ipsum ex, vel dignissim nulla sodales vel. In quis iaculis magna, sit amet imperdiet nisl.

## Sub-Heading A2 3

Vestibulum nec ultricies odio. Nam ipsum nunc, molestie vitae vehicula eget, fermentum at nulla. Vestibulum porta quam vitae urna tincidunt vehicula. Vivamus varius enim in bibendum maximus. Nam at dolor eget mauris laoreet commodo id eu est. Vestibulum faucibus placerat egestas. Nullam semper dui eget purus lacinia rhoncus. Vestibulum sollicitudin vitae ipsum eget auctor. Vivamus congue lorem gravida mi facilisis, ac gravida erat vulputate. Proin pharetra et nunc quis viverra. Proin dignissim consectetur metus nec eleifend. Nullam vitae ex vel lorem efficitur gravida.

## Sub-Heading A2 4

Aliquam convallis libero suscipit metus interdum, non volutpat enim rhoncus. Suspendisse et purus a ex sodales varius in sit amet quam. Aenean vel dui a mi feugiat aliquet in et lacus. Fusce sagittis, nibh eget lobortis tincidunt, leo eros tincidunt est, eu viverra libero purus ac velit. Aliquam vulputate venenatis sem eget vulputate. Integer sed sapien dui. Donec lacinia sed nisi et varius. Phasellus dictum nec justo quis faucibus. Nunc sed elit convallis, scelerisque erat non, tristique nulla. Sed nec maximus lorem, vitae efficitur est. Sed vel augue nisi.

## Sub-Heading A2 5

Pellentesque convallis ullamcorper facilisis. Donec quis justo et risus luctus fringilla a ac augue. Nulla imperdiet hendrerit consequat. Fusce ullamcorper ante vel nulla pharetra, vitae fringilla metus tincidunt. Curabitur convallis non odio a tempus. Nulla nec lectus viverra mauris faucibus efficitur quis a lectus. Etiam aliquam neque tellus, eget euismod lorem cursus ac. Pellentesque sagittis, quam in finibus vestibulum, elit nunc aliquet ex, vel ullamcorper ex tortor eget nunc. Quisque vestibulum turpis nec efficitur commodo. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam maximus a lorem et congue. Curabitur orci purus, auctor et porttitor euismod, porttitor in magna. Duis rhoncus sed nunc sed sagittis. In sed mauris nec augue luctus blandit.

```groovy
def getCruiseControlStatus(String webToolsHost, String encryptionKey) {
    String cruise_control_status = ""
    try {
        cruise_control_status = sh(script: "./run_command_on_ec2_instance.sh ${webToolsHost} ${encryptionKey} 'curl -s localhost:9104/kafkacruisecontrol/state?json=true | jq .MonitorState.state -r'", returnStdout: true).trim()
    } catch (err) {
        cruise_control_status = "FAILED To Retrieve Cruise Control Status, Error: " + err
    }

    return cruise_control_status ? cruise_control_status : "FAILED to get status of cruise control, server possibly down"
}

node('large') {
    timestamps {
        checkout scm
        utils = load './jenkins/groovy_modules/utilities.groovy'
        load './jenkins/groovy_modules/global_vars.groovy'

        // load credentials into environment variables
        withCredentials([usernamePassword(credentialsId: 'svc-accnt', passwordVariable: 'ANSIBLE_VAULT_PASSWORD', usernameVariable: 'ANSIBLE_VAULT_USER')]) {
            creds = utils.loadCredentials()
        }

        wrap([$class: 'BuildUser']) {
            if (env.BUILD_USER_ID) {
                USER = "${BUILD_USER_ID}"
            } else {
                USER = "stp_atlas_wayfinder"
            }
        }

        PR_SAML_ACCOUNT = "${samlAccountPR}"
        PR_IAM_ROLE = "${iamRoleArnPRcontrol}"
        NP_SAML_ACCOUNT = "${samlAccountNP}"
        NP_IAM_ROLE = "${iamRoleArnNP}"

        NP_WEB_TOOLS_HOST = "zk-kafka-web-psup.wayf.emstest.nbn-aws.local"
        PROD_WEB_TOOLS_HOST = "zk-kafka-web-prod.wayf.emsprod.nbn-aws.local"

        checkout([
                $class                           : 'GitSCM',
                branches                         : [[name: 'master']],
                doGenerateSubmoduleConfigurations: false,
                extensions                       : [[$class: 'CloneOption', noTags: false, reference: '', shallow: true], [$class: 'RelativeTargetDirectory', relativeTargetDir: 'api-smoketest']],
                submoduleCfg                     : [],
                userRemoteConfigs                : [[credentialsId: 'svc-accnt', url: "https://git.nbnco.net.au/digital-products/api-smoketest.git"]]
        ])

        dirname = "${env.WORKSPACE}/build-scripts"
        dir(dirname) {
            utils.withSaml2AwsCredentials('aws-creds', "$NP_SAML_ACCOUNT", "$NP_IAM_ROLE") {
                np_instances_to_patch = sh(script: "python -u check_instance_ami_patching.py --max-ami-age 14", returnStdout: true).trim()
                np_cruise_control_status = "Non Prod CruiseControl Status from ${NP_WEB_TOOLS_HOST} is: [" + getCruiseControlStatus(NP_WEB_TOOLS_HOST, "encrypted_ec2_key_np") + "]"
                println np_instances_to_patch
                println np_cruise_control_status
            }
            withCredentials([usernamePassword(credentialsId: 'ado-aws', passwordVariable: 'AWS_PASS', usernameVariable: 'AWS_USER')]) {
                utils.withSaml2AwsCredentials('ado-aws', "$PR_SAML_ACCOUNT", "$PR_IAM_ROLE") {
                    pr_instances_to_patch = sh(script: "python -u check_instance_ami_patching.py --max-ami-age 50", returnStdout: true).trim()
                    prod_cruise_control_status = "Production CruiseControl Status from ${PROD_WEB_TOOLS_HOST} is: [" + getCruiseControlStatus(PROD_WEB_TOOLS_HOST, "encrypted_ec2_key_pr") + "]"
                    println pr_instances_to_patch
                    println prod_cruise_control_status
                }
            }

        }

        dirname = "${env.WORKSPACE}/api-smoketest"
        dir(dirname) {
            try {
                stage('Smoketest NP') {
                    utils.retry_unreliable(3) {
                        sh "./healthcheck.sh nonprod $NONPROD_RECIPIENTS"
                        email_body = sh(script: "cat ./logfile.txt", returnStdout: true).trim() + "\n\n\n" + np_cruise_control_status + "\n\n\n" + np_instances_to_patch
                        println email_body
                        utils.emailLogFile(env.NONPROD_RECIPIENTS, email_body, "Atlas Wayfinder Environment Health Check: Non-Production")
                    }
                }
                stage('Smoketest PR') {
                    utils.retry_unreliable(3) {
                        sh "./healthcheck.sh prod $PROD_RECIPIENTS"
                        email_body = sh(script: "cat ./logfile.txt", returnStdout: true).trim() + "\n\n\n" + prod_cruise_control_status + "\n\n\n" + pr_instances_to_patch
                        utils.emailLogFile(env.PROD_RECIPIENTS, email_body, "Atlas Wayfinder Environment Health Check: Production")
                    }
                }
            } catch (err) {
                utils.emailOnFailure("$USER@nbnco.com.au")
                throw err
            }
        }
    }
}


```
#!/bin/bash
cd "`dirname $0`"

# Variables
base_url="http://localhost:8080"
auth_token="123"  # replace with your actual application key. Can be empty if server does not require authentication
# if an auth token is set to a non-empty value, the server will require authentication
# do this by starting the server with python3 src/main.py --susi_api_key 123

dir_path="/share"
file_path="test.txt"
local_file="local_test.txt"
remote_file="${base_url}/api/data${dir_path}/${file_path}"
index_file="${base_url}/api/data${dir_path}/index.json"
main_index_file="${base_url}/api/data/index.json"

# Generate a file with a random hash
echo "$(date +%s | openssl dgst -sha256 | base64 | head -c 32 ; echo)" > ${local_file}

# Upload the file to the server
echo "Uploading ${local_file} to ${remote_file}"
curl -X POST -H "Authorization: Bearer ${auth_token}" -F "file=@${local_file}" ${remote_file}

# Read the directory /test/index.json
echo "Reading directory ${dir_path}"
curl ${index_file}

# Get the file and compare it to the local file
echo "Comparing the remote file to the local file"
remote_content=$(curl ${remote_file})
echo "Remote content: ${remote_content}"
local_content=$(cat ${local_file})
echo "Local content: ${local_content}"

if [ "$remote_content" = "$local_content" ]
then
    echo "Files are identical (good)"
else
    echo "Files are different (bad)"
fi

# Delete the remote file
echo "Deleting the remote file ${remote_file}"
curl -X DELETE -H "Authorization: Bearer ${auth_token}" ${remote_file}

# Check the /index.json to confirm the subdirectory /test/ does not exist
echo "Checking main index file"
curl ${main_index_file} | grep -q ${dir_path}
if [ $? -eq 0 ]
then
    echo "Directory ${dir_path} still exists (bad)"
else
    echo "Directory ${dir_path} does not exist (good)"
fi

# Delete the local test file
echo "Deleting local test file"
rm ${local_file}

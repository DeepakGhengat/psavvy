# psavvy



![psavvy](https://github.com/DeepakGhengat/psavvy/assets/50538177/22bcd061-d4ba-4f71-8ec1-537bdfeac7f8)

Programmable_Security_Assessment_&_Vulnerabilities_Verification_System (PSAVVY) framework designed for Recon, vulnerabilities scanning and exploitation. It features a comprehensive list of Python3 Lambda Functions, equipped with terminal commands, allowing for targeted scanning and autonomous exploitation. Pronounce as SAVVY.

YOU LOVE ONELINERs, YOU KNOW HOW THE ONELINERs WORKS AND YOU LOVE AUTOMATION IN BUGBOUNTY AND PENTESTING THIS TOOL IS FOR YOU… It is your personal automation container script.

**Why I made PSAVVY?
**

The programs available online they are bulky and if you make changes in them the code get break and it is become so frustrated to patch the code of Tool and run them. That’s why in PSAVVY you find only one psavvy.py file in which you can do whatever you like..

**Comment the lines in psavvy.py file if you don’t want to use the oneliners or tools, and uncomment them whenever you need it.
**

**USAGE:
**

sudo python3 psavvy.py -d target.com


**INSTALLATION NOTICE:
**

ENJOY AUTO INSTALLATION ON YOUR SYSTEM AND EARN GOOD AMOUNTS BY USING PSAVVY.
Use SUDO to install all the tools in the Tools/ Directory
1. sudo apt-get update && sudo apt-get install -y dos2unix (Only use if needed)
2. dos2unix install.sh (Only use if needed)
3. sudo bash install.sh
4. Know your tools, you can visit the psavvy.py or install.sh file to get a broad view on the tools installed in Tools/ Directory or as a binary into your Linux based Distribution
5. Know your tools, is necessary to add some APIs keys to them seperately to so they can run in a proper manner, why the keys have to be seperate, if needed the tools can removed or update that's why. It makes jobs easy.
6. **Config.txt:**

Replace your urls in the config file DO NOT FORGET.

BURP_COLLAB_URL=https://webhook.site/42d36503-e6c7-4a06-a290-5b0bc6d6f64a

BLIND_XSS_URL=https://webhook.site/42d36503-e6c7-4a06-a290-5b0bc6d6f64a

you can declare the variable name in the config.txt file you want to use, you can give any name to the variable you want, and declare it in your tools commands in program (psavvy.py) if needed, as shown below.

For eg:
![image](https://github.com/DeepakGhengat/psavvy/assets/50538177/27a1d77d-357a-4f06-8986-b446fa396291)

If you can see the declaration {get_url_from_config(args.config, 'BURP_COLLAB_URL')}.
you can use the syntax {get_url_from_config(args.config, VARIABLE NAME)}. And declare with any tools you want and if they required the parameter of like that or use as linux terminal command of Tools for eg: ssrf.py -d xyz.com -b BURPCOLLABORATOR_ADDRESS and copy paste in the lambda execute_command function as shown above. Please try to run the psavvy.py file with all the recon tools after all the subdomains and results get collected which is the essential part to run the container, after that you can comment others Lines and  check the specific Vulnerability scanner and Exploitation Tools.


Why I used the lambda Function.
The python3 lambda Function is love… That’s why…..If you open psavvy.py you will the find list of lambda function, anyone can edit and modify the program, make their own a vulnerabilities scanner and exploitation tool.
If you want to modify the program, before that please read…

https://realpython.com/python-lambda/#:~:text=The%20Python%20lambda%20function%20could,n%20set%20at%20definition%20time.

**Importance of Python3 lambda function in project
**

**Normal Function Declaration..
**

Normal functions are defined using the def keyword, followed by the function's name, a list of parameters in parentheses, and a colon. The body of the function is indented below the declaration. These functions can contain multiple expressions and statements, including loops and conditionals.

def add_numbers(a, b):
    return a + b
	
**Lambda Function Declaration..
**


Lambda functions are anonymous functions defined using the lambda keyword. They are syntactically restricted to a single expression. You can have any number of parameters, but only one expression, the result of which is returned by the function.

add_numbers = lambda a, b: a + b

Advantages of Using Lambda Functions
1.	Conciseness: Lambda functions allow you to write functions compactly, reducing the amount of code. They eliminate the need for defining a function with def and naming it, which is especially useful for small, one-off functions that won't be reused.
2.	Inline Definition: Lambda functions can be defined inline, which is handy when passing a simple function as an argument to higher-order functions (functions that take other functions as arguments), such as map(), filter(), and sorted().
3.	Functionality: In contexts where functions are used as syntactical constructs (e.g., in key functions for sorting or for temporary use in higher-order functions), lambda functions can simplify the code by embedding the function definition directly into the code that uses it.
4.	Readability: For simple operations, using lambda functions can improve readability. When used appropriately, they make it immediately clear that the function is a simple, short operation that won't be used elsewhere.

**Code Structure of PSAVVY.
**

![image](https://github.com/DeepakGhengat/psavvy/assets/50538177/0d648327-c048-488f-a18e-c49a3e67cadd)

**Do not forget to add the comma , (after every new command you add). Shown above.
**
If you want to add some functionalities and Commands to psavvy.py file. Follow the below rules and add them.

****Syntax:**
**
![image](https://github.com/DeepakGhengat/psavvy/assets/50538177/7327f527-a61b-4a49-a418-8d05d5e9a32a)


**Note**: The tools lies in the $Tools Directory If you want add some extra tools Add them into the install.sh file and run it. Remember the directory structure and add the commands. Add your new Tool into the install.sh bash script and It will get installed into the $Tools Directory.

**Note:** "{domain}" is a placeholder for the website address (e.g., xyz.com), if we create specific linux terminal based tool commands or a so called oneliners, add them in lambda function in psavvy.py program file so they can run in a program.

for eg: (bash Tools/SubEnum/subenum.sh -d {domain} -r –p).

To save the output we have the $output directory you can use the Linux basics terminal and add your text file in the $output directory with a name you like.
**for eg:**
![image](https://github.com/DeepakGhengat/psavvy/assets/50538177/14f23f95-d18d-43ea-a6e2-4a3461bbf8e7)



**Note:
**

Wordlist:
You can make a changes in the wordlists like Add new payloads, new words, and new DNS resolver, Do not rename the wordlists.

** OS Support:
**
Only Linux Distribution Except the ARCH LINUX for Now(But if you are really a hacker you can modify psavvy.py file for your operating system).

If you are facing any problem, please mention them in issues section.

Thanks to All Cybersecurity Researcher, Big Inspiration for Project 💖





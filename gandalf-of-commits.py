#!/usr/bin/env python

import re
import random

# Define regex patterns for each part of the commit message
jira_pattern = r"[A-Z]+-[0-9]+"
resources_pattern = r"\[.+\]"
message_pattern = r".+"

# Define a list of denied words
denied_words_list = ["stuff", "now", "here", "for better", "additional", "more comments", "more permission",
                     "fixed permissions", "another", "bla", "attempted", "fix error", "fixed name for var",
                     "fixing formatting", "fix wildcard", "formatting updates", "format fixing", "fixed minor error",
                     "fixed items based on feedback", "certain"]

# Define a list of Gandalf phrases
phrases = [
    "Verily, behold the message of your deeds!",
    "You shall not pass...this commit message without review!",
    "Fly, you fools...to the review of this message!",
    "All we have to decide is what to do with the commit message that is given to us.",
    "A wizard is never late, Frodo Baggins. Nor is he early. He commits changes precisely when he means to.",
    "Even the smallest commit message can change the course of the repository.",
    "End? No, the journey doesn't end here. Commit changes must be made. ",
    "I am a servant of the Repository, wielder of the commit messages of Annuminas.",
    "It is not despair, for despair is only for those who see the end beyond all commits.",
    "I have no memory of this commit message.",
    "One does not simply commit changes into Mordor.",
    "May the commit message be with you.",
    "Commit or do not commit, there is no try.",
    "Do not go where the path may lead. Commit where there is no path and leave a trail.",
    "To commit changes is to live, to die is to lose.",
    "In a hole in the repository there lived a commit message.",
    "All that is gold does not commit, not all those who commit are lost.",
    "The commit message that passes the sentence should commit the changes.",
    "The best commit message is the one not written.",
]

# Shuffle the list of Gandalf phrases
random.shuffle(phrases)

# Prompt the user for each part of the commit message
jira = input("Enter the JIRA ticket number: ").strip().upper()
while not re.match(jira_pattern, jira):
    print("Invalid JIRA ticket number.")
    jira = input("Enter the JIRA ticket number: ").strip().upper()

resource_count = int(input("How many resources (roles/policies) are affected? "))
if resource_count < 1:
    print("At least one resource must be affected.")

resources = []
for i in range(resource_count):
    resource_name = input(f"Enter the name of affected resource #{i+1}: ")
    resources.append(resource_name)

message = input("Enter a brief message describing the changes: ").strip()
while any(word in message.lower() for word in denied_words_list):
    print("Please be more descriptive in the commit message.")
    message = input("Enter a brief message describing the changes: ").strip()

commit_message = f"{jira} {', '.join(resources)}: {message}"

# Print the Gandalf phrase and ASCII cloud image
gandalf_phrase = phrases[0]

# Define the ASCII cloud image
cloud = r"""
 _____________________________________________
/ {0:<45} \
|                                             |
 ---------------------------------------------
        \
         \
          \
           Gandalf of The Commits...
""".format(gandalf_phrase)
print(cloud.strip())
print("--------------------------------------------------------------------------------")
print("IMPORTANT: Please ensure that the message accurately reflects the changes made.")
print("IMPORTANT: If your description does NOT match code changes you ARE AT RISK of ")
print("IMPORTANT: Guardians of the HISTORY to DENY your SPELLS !!")
print("--------------------------------------------------------------------------------")
print("Here's your message..\n\n")
print(commit_message)

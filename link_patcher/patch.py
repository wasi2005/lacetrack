html_file = open("index.html", "r")
html_string = html_file.read()
html_list=html_string.split()

for word_index in range(0,len(html_list)):
    word = html_list[word_index]
    if "src" in word or "href" in word:
        print(word)
        start = 0
        for char_index in range(0,len(word)):
            if word[char_index] == '"' or word[char_index] == "'":
                if start == 0:
                    start = char_index+1
                else:
                    end = char_index

        if (":" not in word[start:end]) and (word[start] != "{") and (word[start] != "#") and ("." in word[start:end]):
            url_for = "{{url_for('static',filename='" + word[start:end] + "')}}"
            print(html_list[word_index][:start]+url_for+html_list[word_index][end:])
            html_list[word_index]=html_list[word_index][:start]+url_for+html_list[word_index][end:]

patched_html = " ".join(html_list)

patched_file = open("patched.html", "w+")
patched_file.write(patched_html)

html_file.close()
patched_file.close()

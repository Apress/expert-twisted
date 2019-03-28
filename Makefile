all:
	rm -rf out
	mkdir out
	# hack workaround https://github.com/jgm/pandoc/issues/3752
	cp */*.png out
	(cd out; pandoc --file-scope ../[0-9]*/*.md  -f markdown -o out.docx --reference-docx=../template.docx)
	for d in `ls -d [0-9]*`; do echo $$d ; ( \
		cd $$d;\
		if stat -t *.md >/dev/null 2>&1; then\
			pandoc *.md -f markdown -o ../out/$$d.pdf;\
		fi); done

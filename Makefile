
.POSIX:
.SUFFIXES:
.SUFFIXES: .1 .1.scd

VERSION=0.0.0

PREFIX?=/usr/local
BINDIR?=$(PREFIX)/bin
SHAREDIR?=$(PREFIX)/share/linkchan
MANDIR?=$(PREFIX)/share/man

VPATH=doc

DOCS := \
	linkchanbot.1

all: doc

doc: $(DOCS)

.1.scd.1:
	scdoc < $< > $@

clean:
	$(RM) $(DOCS)

install: all
	mkdir -m755 -p $(DESTDIR)$(BINDIR) $(DESTDIR)$(SHAREDIR) $(DESTDIR)$(MANDIR)/man1
	install -m755 linkchanbot $(DESTDIR)$(BINDIR)/linkchanbot
	install -m644 linkchanbot.1 $(DESTDIR)$(MANDIR)/man1/linkchanbot.1
	install -m644 sample.config/bot.cfg $(DESTDIR)$(SHAREDIR)/bot.cfg
	install -m644 sample.config/alts.json $(DESTDIR)$(SHAREDIR)/alts.json
	install -m644 sample.config/services.json $(DESTDIR)$(SHAREDIR)/services.json
	install -m644 sample.config/queries.json $(DESTDIR)$(SHAREDIR)/queries.json

uninstall:
	$(RM) $(DESTDIR)$(BINDIR)/linkchanbot
	$(RM) $(DESTDIR)$(MANDIR)/man1/linkchanbot.1
	$(RM) $(DESTDIR)$(SHAREDIR)/bot.cfg
	$(RM) $(DESTDIR)$(SHAREDIR)/alts.json
	$(RM) $(DESTDIR)$(SHAREDIR)/services.json
	$(RM) $(DESTDIR)$(SHAREDIR)/queries.json

.PHONY: all doc clean install uninstall

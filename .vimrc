if empty(glob('~/.vim/autoload/plug.vim'))
	silent !curl -fLo ~/.vim/autoload/plug.vim --create-dirs
				\ https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
	autocmd VimEnter * PlugInstall --sync | source $MYVIMRC
endif

call plug#begin('~/.vim/plugged')
Plug 'tpope/vim-fugitive'
Plug 'tpope/vim-surround'
call plug#end()

syntax on
set tabstop=4
set shiftwidth=4
set expandtab
set ai
set incsearch
set number relativenumber
set ruler
highlight Comment ctermfg=green

set path=$PWD/**

noremap gn :bn<cr>
noremap gp :bp<cr>

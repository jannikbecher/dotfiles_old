if empty(glob('~/.vim/autoload/plug.vim'))
	silent !curl -fLo ~/.vim/autoload/plug.vim --create-dirs
				\ https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
	autocmd VimEnter * PlugInstall --sync | source $MYVIMRC
endif

call plug#begin('~/.vim/plugged')
Plug 'tpope/vim-fugitive'
Plug 'tpope/vim-surround'
Plug 'junegunn/fzf', { 'dir': '~/.fzf', 'do': './install --all' }
Plug 'junegunn/fzf.vim'
call plug#end()

let mapleader = ","

syntax on
set tabstop=4
set shiftwidth=4
set expandtab
set ai
set incsearch
set number relativenumber
set ruler
set hidden
set undodir=~/.vim/undodir
set undofile
highlight Comment ctermfg=green

set path=$PWD/**

noremap gn :bn<cr>
noremap gp :bp<cr>

"fzf bindings
nnoremap <Leader>f :GFiles<CR>
nnoremap <Leader>F :Files<CR>
nnoremap <Leader>b :Buffers<CR>
nnoremap <Leader>h :History<CR>
nnoremap <Leader>t :BTags<CR>
nnoremap <Leader>T :Tags<CR>
nnoremap <Leader>l :BLines<CR>
nnoremap <Leader>L :Lines<CR>
nnoremap <Leader>' :Marks<CR>
nnoremap <Leader>/ :Rg<CR>
nnoremap <Leader>H :Helptags!<CR>
nnoremap <Leader>C :Commands<CR>
nnoremap <Leader>: :History:<CR>
nnoremap <Leader>M :Maps<CR>
nnoremap <Leader>s :Filetypes<CR>

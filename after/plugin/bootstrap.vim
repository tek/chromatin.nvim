let s:cache_dir = exists('$XDG_CACHE_HOME') ? $XDG_CACHE_HOME : $HOME . '/.cache'
let s:data_dir = exists('$XDG_DATA_HOME') ? $XDG_DATA_HOME : $HOME . '/.local/share'
let s:default_venvs = s:cache_dir . '/chromatin/venvs'
let s:venvs = get(g:, 'chromatin_venv_dir', s:default_venvs)
let s:venv = s:venvs . '/chromatin'
let s:scripts = fnamemodify(expand('<sfile>'), ':p:h:h:h') . '/scripts'
let s:ghc_version = '8.6.3'
let s:ghc = 'ghc-' . s:ghc_version
let s:chromatin_haskell_version = '0.1.0.0'
let s:hs_base = s:data_dir . '/chromatin-hs'
let s:install_ghcup_cmd = s:scripts . '/install-ghcup'
let s:bin = $HOME . '/.ghcup/bin'
let s:ghcup_exe = s:bin . '/ghcup'
let s:ghc_exe = s:bin . '/' . s:ghc
let s:cabal_exe = s:bin . '/' . 'cabal'
let s:crm_hs_exe = $HOME . '/.cabal/bin/chromatin'
let s:termbuf = -1

function! s:close_terminal() abort "{{{
  execute 'silent! ' . s:termbuf . 'bwipeout!'
  let s:termbuf = -1
endfunction "}}}

function! s:job_finished(success, error, code) abort "{{{
  if a:code == 0
    call s:close_terminal()
    call call(a:success, [])
  else
    echohl Error
    echom 'chromatin: ' . a:error
    echohl None
  endif
endfunction "}}}

function! s:job(cmd, output, next, error) abort "{{{
  let output = s:tempdir . '/' . a:output
  call jobstart(a:cmd . ' &> ' . output, { 'on_exit': { i, c, e -> s:job_finished(a:next, a:error, c) } })
  sleep 100m
  execute '15split term://tail -f ' . output
  let s:termbuf = bufnr('%')
  silent! wincmd w
endfunction "}}}

function! s:run_chromatin() abort "{{{
  return jobstart(s:crm_hs_exe, { 'rpc': v:true })
endfunction "}}}

function! s:install_chromatin() abort "{{{
  echom 'chromatin: installing chromatin…'
  return s:job(s:cabal_exe . ' v1-install chromatin', 'install-chromatin', 's:run_chromatin', 'failed to install chromatin')
endfunction "}}}

function! s:install_cabal() abort "{{{
  echom 'chromatin: installing cabal-install…'
  return s:job(s:ghcup_exe . ' install-cabal', 'install-cabal', 's:install_cabal', 'failed to install cabal')
endfunction "}}}

function! s:install_ghc() abort "{{{
  echo 'chromatin: installing ghc. this may take a minute…'
  return s:job(s:ghcup_exe . ' install ' . s:ghc_version, 'install-ghc', 's:install_cabal', 'failed to install ghc')
endfunction "}}}

function! s:install_ghcup() abort "{{{
  echom 'chromatin: installing ghcup…'
  return s:job(s:install_ghcup_cmd, 'install-ghcup', 's:install_ghc', 'failed to install ghcup')
endfunction "}}}

function! s:bootstrap() abort "{{{
  autocmd! ChromatinBootstrap
  if filereadable(s:crm_hs_exe)
    return
  endif
  let s:tempdir = tempname()
  call system('mkdir ' . s:tempdir)
  if filereadable(s:ghc_exe)
    if filereadable(s:cabal_exe)
      return s:install_chromatin()
    else
      return s:install_cabal()
    endif
  elseif filereadable(s:ghcup_exe)
    return s:install_ghc()
  else
    return s:install_ghcup()
  endif
endfunction "}}}

" if get(g:, 'chromatin_autobootstrap', 1)
"   if get(g:, 'chromatin_haskell', 0) || $CHROMATIN_HASKELL != ''
"     augroup ChromatinBootstrap
"       autocmd VimEnter * nested call s:bootstrap()
"     augroup END
"   endif
" endif
